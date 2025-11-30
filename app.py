from flask import Flask, render_template, request, jsonify
import random, string, requests, re, threading, time

app = Flask(__name__)

proxies = []

def update_proxies():
    global proxies
    while True:
        try:
            sources = [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
                "https://www.proxy-list.download/api/v1/get?type=http",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
            ]
            new = []
            for url in sources:
                try:
                    r = requests.get(url, timeout=10)
                    for line in r.text.splitlines():
                        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line.strip()):
                            new.append(line.strip())
                except: pass
            proxies = list(set(new))
            print(f"[KHAHUB] {len(proxies)} proxies loaded")
        except: pass
        time.sleep(300)

threading.Thread(target=update_proxies, daemon=True).start()

def rand_str(n=16): return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
def rand_ip(): return ".".join(str(random.randint(0,255)) for _ in range(4))

@app.route('/')
def home(): return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    code = request.json.get('code', '')
    lines = [l.strip() for l in code.split('\n') if l.strip()]
    output = ""
    vars = {}
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith('create <web>'):
            output += '<div class="web-container">'

        elif line.startswith('show <html>'):
            html = ""
            i += 1
            while i < len(lines) and not lines[i].startswith('</html>'):
                html += lines[i] + "\n"
                i += 1
            output += f'<div class="editable" contenteditable="true">{html}</div>'

        elif line.startswith('change <html with changes>'):
            html = ""
            i += 1
            while i < len(lines) and not lines[i].startswith('</html>'):
                html += lines[i] + "\n"
                i +=  += 1
            output += f'<div class="editable" contenteditable="true" style="background:rgba(0,150,255,0.2)">{html}</div>'

        elif line.startswith('add(random(math:'):
            if 'letters' in line and 'numbers' in line:
                vars['last'] = rand_str(16)
            elif 'ip' in line:
                vars['last'] = rand_ip()
            output += f"<span style='color:#ffcc00;'>[+] {vars['last']}</span><br>"

        elif line.startswith('repeat '):
            count = int(line.split()[1])
            body_start = i + 1
            depth = 1
            while i < len(lines):
                i += 1
                if 'repeat' in lines[i]: depth += 1
                if 'if end' in lines[i]: depth -= 1
                if depth == 0: break
            for _ in range(count):
                for cmd in lines[body_start:i]:
                    if 'random(proxy)' in cmd:
                        p = random.choice(proxies) if proxies else "NO_PROXY"
                        output += f"[BOT] Proxy → {p}<br>"
                    elif 'log(' in cmd:
                        msg = cmd.split('log(')[1].split(')')[0].strip("'\"")
                        output += f"[LOG] {msg}<br>"

        elif line.startswith('local '):
            name, val = line[6:].split('=',1)
            vars[name.strip()] = val.strip().strip("'\"")
            output += f"[LOCAL] {name} = {val}<br>"

        i += 1

    return jsonify({
        'output': output or "<h2 style='color:#0f0'>KHAHUB READY – Write some code boss</h2>",
        'proxy_count': len(proxies)
    })

if __name__ == '__main__':
    print("KHAHUB LAUNCHED FOR KHALED")
    app.run(host='0.0.0.0', port=1337)