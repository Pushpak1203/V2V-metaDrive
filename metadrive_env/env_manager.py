# metadrive_env/env_manager.py

from metadrive import MetaDriveEnv


def start_metadrive(vehicle_ids):
    """
    Launch a MetaDrive simulation with given vehicle IDs.
    """
    env = MetaDriveEnv({
        "use_render": True,          # ✅ open simulation GUI
        "manual_control": False,     # automatic agents
        "num_agents": len(vehicle_ids),
        "start_seed": 5,
        "num_scenarios": 1
    })

    obs, info = env.reset()
    done = False

    print(f"[SIM] MetaDrive simulation started with vehicles: {vehicle_ids}")

    try:
        while not done:
            # Let each vehicle take random actions for now
            actions = {agent_id: env.action_space.sample() for agent_id in vehicle_ids}
            obs, rewards, terminated, truncated, info = env.step(actions)
            env.render()

            # Check if all agents are done
            if all(terminated.values()):
                done = True
    except KeyboardInterrupt:
        print("[SIM] MetaDrive simulation interrupted by user.")
    finally:
        env.close()
        print("[SIM] MetaDrive simulation closed.")
