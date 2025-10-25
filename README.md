# Prometheus & Alertmanager Integration with Docker

## Overview
This project demonstrates the setup of **Prometheus** and **Alertmanager** with a Flask web application using **Docker Compose**, along with **network restrictions via iptables** and **container restart policies**.  
The exercise verifies monitoring functionality, alert propagation, and Docker’s built-in self-healing behavior.

---

## 1. Project Structure
```
nadinsoftTask/
├─ docker-compose.yml
├─ prometheus.yml
├─ alerts.yml
├─ alertmanager.yml
└─ app/ (Flask source)
```

---

## 2. Docker Compose Setup

### Services
- **web** – Flask application exposing `/metrics` on port **5000**
- **prometheus** – Collects metrics and evaluates alert rules (port **9090**)
- **alertmanager** – Receives and groups alerts (port **9093**)

Each service uses:
```yaml
restart: always
```
to ensure automatic recovery on failure or system reboot.

### Launch
```bash
docker compose up -d
```
Check status:
```bash
docker compose ps
```

---

## 3. Prometheus Configuration (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/alerts.yml

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "flask-app"
    metrics_path: /metrics
    static_configs:
      - targets: ["web:5000"]

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
```

---

## 4. Alerts Definition (`alerts.yml`)
```yaml
groups:
  - name: demo
    rules:
      - alert: Demo_AlwaysOn
        expr: vector(1)
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "Demo alert"
          description: "Test alert for validation"

      - alert: AppDown
        expr: up{job="flask-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Flask App is down"
          description: "The Flask app target is not responding"
```

---

## 5. Verifying Monitoring Setup

- **Targets Page:**  
  `http://<server_ip>:9090/targets` → both `prometheus` and `flask-app` should show *UP*.
- **Graph Page:**  
  Run queries such as:
  ```
  up{job="flask-app"}
  process_resident_memory_bytes{job="flask-app"}
  rate(http_requests_total{job="flask-app"}[1m])
  ```
- **Alerts Page:**  
  `http://<server_ip>:9090/alerts` → `Demo_AlwaysOn` should appear as *Firing*.
- **Alertmanager UI:**  
  `http://<server_ip>:9093` → same alert visible.

---

## 6. Restricting External Access (iptables)

### Objective
Allow Prometheus and Alertmanager access **only from localhost and internal Docker network**, denying external clients.

### Applied Rules
```bash
sudo iptables -I DOCKER-USER 1 -s 172.18.0.0/16 -d 172.18.0.0/16 -j RETURN
sudo iptables -I DOCKER-USER 2 -p tcp -s 127.0.0.1 --dport 9090 -j RETURN
sudo iptables -I DOCKER-USER 3 -p tcp -s 127.0.0.1 --dport 9093 -j RETURN
sudo iptables -I DOCKER-USER 4 -p tcp -s 172.16.109.136 --dport 9090 -j RETURN
sudo iptables -I DOCKER-USER 5 -p tcp -s 172.16.109.136 --dport 9093 -j RETURN
sudo iptables -A DOCKER-USER -p tcp --dport 9090 -j DROP
sudo iptables -A DOCKER-USER -p tcp --dport 9093 -j DROP
```

### Result
| Test | Result |
|------|---------|
| `curl localhost:9090` | ✅ 200 / 405 (works locally) |
| Browser from external host | ❌ Connection timeout |
| Prometheus ↔ Alertmanager | ✅ Internal communication allowed |

---

## 7. Demonstrating Restart Policy

### Step 1 – Simulate a crash
```bash
mv prometheus.yml prometheus_bad.yml
echo "invalid config" > prometheus.yml
docker restart nadinsofttask-prometheus-1
```

### Step 2 – Observe automatic restarts
```bash
watch -n1 docker ps
```
Output example:
```
nadinsofttask-prometheus-1   prom/prometheus:v2.54.0   Restarting (1) 5 seconds ago
```

### Step 3 – Restore normal state
```bash
mv prometheus_bad.yml prometheus.yml
docker restart nadinsofttask-prometheus-1
```

### Verification
Prometheus returns to `Up` status automatically, proving `restart: always` works as expected.

---

## 8. Screenshots to Include
1. **Prometheus Targets** (all UP)  
2. **Graph** page with live metrics  
3. **Alerts** page showing firing rules  
4. **Alertmanager UI** with firing alert  
5. **iptables rules** output  
6. **docker ps** showing `Restarting (1)` then `Up`

---

## 9. Conclusion
This lab demonstrates:
- Successful integration of Prometheus and Alertmanager with Dockerized Flask app  
- Custom alerting and target scraping  
- Secure access control using iptables (DOCKER-USER chain)  
- Reliable self-healing via Docker restart policies  

> ✅ The setup provides a fully functional, monitored, and self-recovering environment.
