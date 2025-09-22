# MetaDrive + V2V Communication System 🚗📡

This project integrates **MetaDrive simulation** with a **Vehicle-to-Vehicle (V2V) communication system**.  
It allows multiple simulated vehicles to exchange encrypted state information (position, speed, obstacles) over UDP sockets and make safe driving decisions using a **decision engine**.

---

## 📂 Project Structure

```
metaDrive+V2V/
│
├── communication/              # Networking layer
│   ├── broadcaster.py          # Sends vehicle state messages
│   └── receiver.py             # Receives and processes messages
│
├── decision_engine/            # Decision-making logic
│   ├── response_planner.py     # Chooses actions based on thresholds
│   ├── hybrid_astar.py         # Path planning
│   └── motion_primitives.py    # Maneuver library
│
├── config/                     # Configuration files
│   ├── sim_params.yaml         # Simulation settings
│   ├── thresholds.yaml         # Safety thresholds
│   └── v2v_settings.yaml       # Communication & encryption configs
│
├── metadrive_env/              # MetaDrive environment management
│   ├── env_manager.py
│   └── vehicle_manager.py
│
├── encryption/                 # Security layer
│   ├── encryption_utils.py     # AES encryption/decryption
│   └── secret.key              # Auto-generated key (if missing)
│
├── run_all.py                  # Master script to launch sim + comms
└── requirements.txt            # Python dependencies
```

---

## ⚙️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Pushpak1203/V2V-metaDrive.git
   cd V2V-metaDrive
   ```

2. Create & activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scriptsctivate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Simulation

Start the entire system (MetaDrive + broadcasters + receivers):

```bash
python run_all.py
```

### Command-line options:
- `--sim_type` : Choose simulation backend (default: `metadrive`)
- `--vehicle_ids` : List of vehicle IDs to simulate (overrides `sim_params.yaml`)
- `--broadcast_port` : UDP port for broadcasting messages
- `--receiver_base_port` : Base UDP port for receivers

Example:
```bash
python run_all.py --vehicle_ids ego_vehicle vehicle_1 vehicle_2 --broadcast_port 5000 --receiver_base_port 5001
```

---

## 🔒 Security Layer

- Messages between vehicles are **AES-256 encrypted**.
- Encryption key is stored in `config/v2v_settings.yaml` (must be Base64 encoded).
- If no key exists, `encryption_utils.py` can generate one automatically.

---

## ⚡ Features

- ✅ Multi-vehicle communication over UDP
- ✅ Encrypted message exchange (AES-256)
- ✅ Configurable safety thresholds
- ✅ Decision-making engine (Hybrid A* + motion primitives)
- ✅ Extensible simulation backend (MetaDrive)

---

## 🧪 Example Output

When running `run_all.py`, you should see:

```
[MASTER] MetaDrive environment will be started by env_manager.
[MASTER] Starting broadcaster for ego_vehicle...
[ENCRYPTION] AES key loaded successfully (256-bit).
[BROADCASTER] ego_vehicle broadcasting on port 5000
[RECEIVER] Vehicle ego_vehicle listening on port 5001
[RECEIVER] Action for ego_vehicle: SLOW_DOWN
```

---

## 👨‍💻 Author
**Pushpak Chakraborty**  
AI & Simulation Enthusiast 🚀

---

## 📜 License
MIT License. Free to use and modify.
