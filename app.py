from flask import Flask, render_template, request, send_file
import qrcode
import os
import uuid
import random

app = Flask(__name__)

def generate_random_ipv4():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def generate_random_ipv6():
    return ":".join(f"{random.randint(0, 65535):x}" for _ in range(8))

def create_random_dns_entry():
    domain = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8)) + ".paladin"
    ip4 = generate_random_ipv4()
    ip6_1 = generate_random_ipv6()
    ip6_2 = generate_random_ipv6()
    return {
        "domain": domain,
        "IPv4": ip4,
        "IPv6_1": ip6_1,
        "IPv6_2": ip6_2
    }

def generate_key_pair():
    private_key = uuid.uuid4().hex
    public_key = uuid.uuid4().hex
    return private_key, public_key

def create_wireguard_config(username, dns_type):
    dns_entry = create_random_dns_entry()
    private_key, public_key = generate_key_pair()
    dns = dns_entry["IPv4"] if dns_type == "4" else dns_entry["IPv6_1"]
    user_ip = f"10.0.0.{random.randint(2, 254)}"

    config_content = f"""
[Interface]
PrivateKey = {private_key}
Address = {user_ip}/24
DNS = {dns}

[Peer]
PublicKey = SERVER_PUBLIC_KEY_PLACEHOLDER
Endpoint = kcokgwws.paladin:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

    filename = f"configs/{username}.conf"
    os.makedirs("configs", exist_ok=True)
    with open(filename, "w") as f:
        f.write(config_content.strip())

    return filename, config_content

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        dns_type = request.form["dns"]
        conf_path, conf_text = create_wireguard_config(username, dns_type)

        qr_path = f"configs/{username}_qr.png"
        qr = qrcode.make(conf_text)
        qr.save(qr_path)

        return render_template("result.html", username=username, conf_file=conf_path, qr_file=qr_path)

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    return send_file(f"configs/{filename}", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
