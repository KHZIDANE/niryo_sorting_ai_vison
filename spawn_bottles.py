#!/usr/bin/env python3
"""
spawn_bottles.py
----------------
Spawns N random bottles on the inspection marker (x≈0.15, y≈0.0).
Run manually: python3 spawn_bottles.py --count 3 --type random
Or: python3 spawn_bottles.py --type good   (force all good)
     python3 spawn_bottles.py --type defective
"""
import argparse
import os
import random
import subprocess
import time

MODELS_PATH = os.path.expanduser(
    '~/niryo_iws/src/niryo_gazebo/models')

PICK_ZONE = {'x': 0.15, 'y': 0.0, 'z': 0.46}
SPREAD    = 0.04   # ± metres so bottles don't stack perfectly

def sdf_path(model_name):
    return os.path.join(MODELS_PATH, model_name, 'model.sdf')

def spawn(name, model, x, y, z, idx):
    cmd = [
        'gz', 'service', '-s', '/world/sorting_world/create',
        '--reqtype', 'gz.msgs.EntityFactory',
        '--reptype', 'gz.msgs.Boolean',
        '--timeout', '2000',
        '--req',
        f'sdf_filename: "{sdf_path(model)}", '
        f'name: "{name}_{idx}", '
        f'pose: {{position: {{x: {x}, y: {y}, z: {z}}}}}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'  Spawned {name}_{idx} at ({x:.3f}, {y:.3f}, {z})')
    else:
        print(f'  Failed to spawn {name}_{idx}: {result.stderr.strip()}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=2)
    parser.add_argument('--type', choices=['good', 'defective', 'random'],
                        default='random')
    args = parser.parse_args()

    for i in range(args.count):
        model = {
            'good':      'bottle_good',
            'defective': 'bottle_defective',
            'random':    random.choice(['bottle_good', 'bottle_defective']),
        }[args.type]

        x = PICK_ZONE['x'] + random.uniform(-SPREAD, SPREAD)
        y = PICK_ZONE['y'] + random.uniform(-SPREAD, SPREAD)
        spawn('bottle', model, x, y, PICK_ZONE['z'], i)
        time.sleep(0.3)   # let physics settle between spawns

if __name__ == '__main__':
    main()
