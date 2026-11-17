# DevOps Automation Stack

A small Flask API deployed to a local Ubuntu VM with **one command**. Ansible configures the server, Docker Compose runs the app and its observability stack, and a GitLab CI pipeline tests, builds and scans the image.

> Everything runs locally and costs nothing. No cloud account is needed.

## What it demonstrates

| Area | Tool |
|---|---|
| Server configuration (idempotent) | Ansible roles: `common`, `docker`, `nginx`, `stack` |
| Reverse proxy and firewall | Nginx, UFW |
| Containers | Docker, Docker Compose |
| Metrics and alerting | Prometheus (alert rules `AppDown`, `HighErrorRate`) and Grafana |
| Centralised logs | Loki and Promtail, searched in Grafana |
| CI | GitLab CI: pytest, Ansible syntax check, image build, Trivy scan |

## Architecture

```
Browser -> :8080 -> Nginx (VM :80) -> app container (:5000)
                                        |-- /metrics ----> Prometheus -> alerts
                                        '-- stdout logs -> Promtail -> Loki
                                                         Grafana reads both
```

(Replace this block with a draw.io diagram and add it to `docs/architecture.png`.)

## Run it

You need VirtualBox and Vagrant installed (works on Windows without WSL, because Ansible runs inside the VM). About 3 GB of free RAM is needed.

```bash
git clone <your-repo-url>
cd devops-automation-stack
vagrant up          # first run takes 10-15 minutes
```

| What | URL |
|---|---|
| App (through Nginx) | http://localhost:8080 |
| Health check | http://localhost:8080/health |
| Prometheus and alerts | http://localhost:9090/alerts |
| Grafana (admin / admin, change it) | http://localhost:3000 |

Run the tests without the VM:

```bash
pip install -r app/requirements-dev.txt
pytest app -v
```

## Verify idempotency

```bash
vagrant provision
```

The second run should show almost no changes (`changed=0` for most tasks). That proves the playbook describes a state and does not blindly repeat commands.

## Failure test (do this and document it)

1. Open http://localhost:9090/alerts and confirm both alerts are green.
2. `vagrant ssh`, then `docker stop app`.
3. Within about 20 seconds, `AppDown` turns **Firing** in Prometheus.
4. In Grafana, go to Explore, choose Loki, and run `{container="app"}` to see the app's last logs.
5. `docker start app` and watch the alert clear.
6. For the error alert, run `for i in $(seq 1 100); do curl -s localhost:8080/boom > /dev/null; done` and watch `HighErrorRate`.
7. Write down what you saw and how long recovery took, in `docs/failure-test.md`, with screenshots.

## Next improvements

- Add Alertmanager and send the alerts to Telegram or email.
- Add a Grafana dashboard for request rate, error rate and latency (export it as JSON into `monitoring/grafana/provisioning`).
- Create the VM with Terraform instead of Vagrant, or apply the same playbook to a real cloud server.
- Add Ansible Vault for the Grafana admin password.

## Security notes

- Ports 3000 and 9090 are open for the lab only. Do not expose them on a real server.
- Change the default Grafana password. Never commit `.env` files, keys or real IP addresses.
- The firewall (UFW) allows only SSH, HTTP, Grafana and Prometheus.
