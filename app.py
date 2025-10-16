from flask import Flask, render_template, request, jsonify, Response
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
import logging
import uuid


# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Pool de opções reutilizáveis
def get_chrome_options():
    """Retorna opções otimizadas do Chrome"""
    options = Options()
    
    # Modo headless e performance
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--window-size=1920,1080')
    
    # Desabilita recursos desnecessários para performance
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')  # Não carrega imagens
    options.add_argument('--disable-css')  # Não carrega CSS
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-java')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-javascript')  # Se não precisar de JS
    
    # Logging e debugging
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    
    # Otimizações de rede
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--mute-audio')
    options.add_argument('--no-first-run')
    options.add_argument('--safebrowsing-disable-auto-update')
    
    # User data dir ÚNICO para cada instância
    unique_id = uuid.uuid4()
    options.add_argument(f'--user-data-dir=/tmp/chrome-{unique_id}')
    
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('prefs', {
        'profile.default_content_setting_values.notifications': 2,
        'profile.managed_default_content_settings.images': 2,
        'disk-cache-size': 4096
    })
    
    return options

class LoginAutomation:
    def __init__(self, login_id):
        self.login_id = login_id
        self.username = "tomsmith"
        self.password = "SuperSecretPassword!"
        self.url = "https://the-internet.herokuapp.com/login"
        
    def setup_driver(self):
        """Configura o WebDriver Chrome otimizado"""
        driver = webdriver.Chrome(options=get_chrome_options())
        driver.set_page_load_timeout(15)  # Timeout mais curto
        driver.implicitly_wait(5)
        return driver
    
    def perform_login(self):
        """Executa o login e retorna o resultado"""
        driver = None
        start_time = time.time()
        
        try:
            driver = self.setup_driver()
            driver.get(self.url)
            
            wait = WebDriverWait(driver, 8)  # Timeout reduzido
            
            # Login
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.username)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Verifica sucesso
            wait.until(EC.url_contains("/secure"))
            
            success_message = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success"))
            )
            
            # Token
            cookies = driver.get_cookies()
            token = next((cookie['value'] for cookie in cookies if cookie['name'] == 'rack.session'), 'N/A')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                'login_id': self.login_id,
                'status': 'SUCESSO',
                'token': token[:20] + '...' if len(token) > 20 else token,
                'time': round(execution_time, 2),
                'message': success_message.text.strip()
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.error(f"Login {self.login_id} falhou: {str(e)}")
            
            return {
                'login_id': self.login_id,
                'status': 'FALHA',
                'token': 'N/A',
                'time': round(execution_time, 2),
                'message': str(e)[:100]
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

def generate_login_stream(num_logins):
    """Gera stream de eventos para atualização em tempo real"""
    start_time = time.time()
    results = []
    
    yield f"data: {json.dumps({'type': 'start', 'num_logins': num_logins, 'timestamp': datetime.now().isoformat()})}\n\n"
    
    # Limita workers para não sobrecarregar
    max_workers = min(num_logins, 10)  # Máximo 10 paralelos
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        login_tasks = [LoginAutomation(i+1) for i in range(num_logins)]
        futures = [executor.submit(task.perform_login) for task in login_tasks]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            yield f"data: {json.dumps({'type': 'progress', 'result': result})}\n\n"
    
    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    
    results.sort(key=lambda x: x['login_id'])
    
    success_count = sum(1 for r in results if r['status'] == 'SUCESSO')
    fail_count = sum(1 for r in results if r['status'] == 'FALHA')
    
    summary = {
        'type': 'complete',
        'total_time': total_time,
        'success_count': success_count,
        'fail_count': fail_count,
        'success_rate': round((success_count/num_logins)*100, 1),
        'results': results
    }
    
    yield f"data: {json.dumps(summary)}\n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_logins():
    try:
        num_logins = int(request.json.get('num_logins', 0))
        
        if num_logins <= 0:
            return jsonify({'error': 'O número de logins deve ser maior que zero'}), 400
        
        return Response(
            generate_login_stream(num_logins),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except ValueError:
        return jsonify({'error': 'Valor inválido'}), 400
    except Exception as e:
        logger.error(f"Erro na execução: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)