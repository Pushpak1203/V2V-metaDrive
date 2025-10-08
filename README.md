# MetaDrive + V2V Communication Project

This project integrates the [MetaDrive Simulator](https://metadrive-simulator.readthedocs.io/) with a **Vehicle-to-Vehicle (V2V) communication system**.  
It demonstrates **encrypted broadcasting and receiving of vehicle states** while simulating autonomous driving behaviors in a virtual world.

---

## 🚗 Features
- **MetaDrive Simulation** – vehicles driving in a virtual environment.
- **V2V Communication** – broadcaster and receiver modules exchange vehicle state.
- **AES-256 Encryption** – secure communication using Base64 keys.
- **Decision Engine** – simple planner that decides whether to `BRAKE`, `SLOW_DOWN`, or `KEEP_GOING`.
- **Configurable Parameters** – simulation, V2V, and thresholds configurable via YAML.
- **Modular Codebase** – separated into `communication/`, `decision_engine/`, and `metadrive_env/`.

---

## 📂 Project Structure

```
META-DRIVE+V2V/
│
├── metadrive/                      
│   ├── __init__.py
│   ├── assets/
│   ├── base_class/
│   ├── component/
│   ├── engine/
│   ├── envs/
│   ├── examples/
│   │   ├── run_lowcost_policy.py
│   │   ├── drive_in_multi_agent_env.py
│   │   └── ...
│   ├── manager/
│   ├── obs/
│   ├── policy/
│   ├── render_pipeline/
│   ├── scenario/
│   ├── shaders/
│   ├── tests/
│   ├── third_party/
│   ├── utils/
│   ├── version.py
│   └── setup.py
│
├── communication/
│   ├── broadcaster.py
│   ├── receiver.py
│   ├── encryption.py
│   └── message_format.py
│
├── config/
│   ├── sim_params.yaml
│   ├── thresholds.yaml
│   └── v2v_settings.yaml
│
├── decision_engine/
│   ├── hybrid_astar.py
│   ├── motion_primitives.py
│   └── response_planner.py
│
├── encryption/
│   ├── encryption_utils.py
│   └── secret.key
│
├── metadrive_env/
│   ├── env_manager.py
│   └── vehicle_manager.py
│
├── logs/
│
├── requirements.txt
├── run_all.py
└── README.md

```

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Encryption Key
The `v2v_settings.yaml` must contain a **Base64-encoded AES key**.

Generate one:
```bash
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

Paste it into `config/v2v_settings.yaml`:
```yaml
encryption_key: "YOUR_BASE64_KEY_HERE"
```

---

## ▶️ Running the Simulation

Launch everything (MetaDrive + broadcasters + receivers):

```bash
python run_all.py
```

---

## ✅ Expected Output

When running, you should see:
```bash
[MASTER] MetaDrive environment will be started by env_manager.
[MASTER] Starting broadcaster for ego_vehicle...
[ENCRYPTION] AES key loaded successfully (256-bit).
[BROADCASTER] ego_vehicle broadcasting on port 5000
[RECEIVER] Vehicle ego_vehicle listening on port 5001
[RECEIVER] Action for ego_vehicle: SLOW_DOWN
```

And you will also get a **MetaDrive simulation window** showing the virtual driving environment.  
Vehicles exchange their states via V2V while the decision engine reacts in real-time.

---

## 🛠️ Testing Step-by-Step

1. Check configs:
   ```bash
   cat config/sim_params.yaml
   cat config/v2v_settings.yaml
   cat config/thresholds.yaml
   ```

2. Run only MetaDrive (no comms):
   ```bash
   python -m metadrive_env.env_manager
   ```

3. Run broadcaster or receiver individually:
   ```bash
   python communication/broadcaster.py --vehicle_id ego_vehicle --sim_type metadrive --broadcast_port 5000 --v2v_config config/v2v_settings.yaml
   python communication/receiver.py --vehicle_id ego_vehicle --sim_type metadrive --listen_port 5001 --v2v_config config/v2v_settings.yaml --thresholds config/thresholds.yaml
   ```

---

## 📌 Notes
- Make sure **MetaDrive** is properly installed (see `requirements.txt`).
- Run `run_all.py` only from the **project root**.
- If encryption errors appear, regenerate a valid Base64 key.
- Logs are stored under `logs/`.

---

## ✨ Future Improvements
- Visualization of V2V messages.
- More advanced decision-making (Reinforcement Learning).
- Cloud-based simulation (Google Colab / GPU).
