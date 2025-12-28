import math

def get_gear_ratio(x: float, v: float, slope: float, mu: float, track_info: dict) -> float:
    """
    Stark Industries - Eco-Gear Controller (Final Submission Version)
    
    SYSTEM ARCHITECTURE:
    1. Gravity-First Energy Recovery: Utilizes negative slopes for zero-cost momentum.
    2. Predictive Gradient Adjustment: Analyzes 'next_segment' to pre-accelerate for hills.
    3. Traction-Limited Torque: Scales gear ratio by friction (mu) to prevent wheel-spin.
    4. Velocity-Targeting: Maintains a 6.0 m/s 'sweet spot' for time-limit compliance.
    """
    
    # --- 1. Operational Constants ---
    MAX_ALLOWED_GEAR = 5.0
    MIN_POWER_GEAR = 0.4
    TARGET_VELOCITY = 6.0    # Target speed in m/s for optimal efficiency/time balance
    STALL_VELOCITY = 0.5     # Threshold to prevent complete immobilization
    LOOK_AHEAD_DIST = 12.0   # Look-ahead window in meters
    
    # --- 2. Downhill Strategy (Kinetic Energy Recovery) ---
    # If the gradient is negative, we disable the engine to coast.
    # Energy consumption at gear_ratio 0.0 is zero.
    if slope < -0.02:
        if v < STALL_VELOCITY:
            return MIN_POWER_GEAR # Small nudge if stuck on a minor dip
        return 0.0

    # --- 3. Predictive Look-Ahead (Strategic Preparation) ---
    # Anticipate upcoming terrain transitions to manage momentum proactively.
    gear_override = None
    next_seg = track_info.get('next_segment')
    
    if next_seg:
        # Tuple unpacking as per main.py structure: (start, end, slope, mu)
        n_start, n_end, n_slope, n_mu = next_seg
        dist_to_next = n_start - x
        
        # Prepare for Significant Inclines (>15% grade)
        if n_slope > 0.15 and dist_to_next < LOOK_AHEAD_DIST:
            # Shift to a high-torque ratio early to build kinetic energy
            gear_override = 3.5 
            
        # Prepare for Low-Friction Zones (Icy/Sandy patches)
        elif n_mu < 0.4 and dist_to_next < 5.0:
            # Lower the gear early to reduce torque and prevent slipping at entry
            gear_override = 1.2

    # --- 4. Real-Time Terrain Response ---
    if gear_override is not None:
        gear_output = gear_override
    else:
        # Reactive logic based on current slope
        if slope > 0.2:
            gear_output = 4.0   # Steep climb: High torque required
        elif slope > 0.05:
            gear_output = 2.0   # Moderate incline: Steady climb
        else:
            # Flat terrain: Velocity maintenance logic
            if v < TARGET_VELOCITY:
                gear_output = 1.2 # Gentle acceleration to target
            else:
                gear_output = 0.5 # Low-power maintenance gear

    # --- 5. Dynamic Traction Control (Slip Prevention) ---
    # Prevents energy-wasting wheel spin by capping torque based on available grip.
    # Max safe gear is linearly scaled by friction mu.
    traction_limit = mu * 5.0 
    gear_output = min(gear_output, traction_limit)

    # --- 6. Failsafe Protocols ---
    # Anti-Stall: If velocity is near zero on non-downhill terrain, force torque.
    if v < STALL_VELOCITY and slope >= -0.02:
        gear_output = max(gear_output, 3.0)
        
    # High-Velocity Cutoff: Prevent over-speeding to protect energy budget.
    if v > 12.0:
        return 0.0

    # Final Output Validation
    return float(max(0.0, min(gear_output, MAX_ALLOWED_GEAR)))