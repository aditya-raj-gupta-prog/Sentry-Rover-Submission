<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">

</head>
<body>

<h1>IMPORTANT!!! READ THE FILE BEFORE ATTEMPTING THE CHALLENGE</h1>
<h1>Eco-Gear Challenge Simulator</h1>

<p>
  A Python-based simulation environment for developing
  <strong>energy-efficient gear-shifting strategies</strong>
  for a bicycle-style rover.

  NOTE: <strong>Read the README_CODE.md file (right click and select open preview in VS Code) to understand how the simulator works.</strong>
</p>

<p>
  Your task: implement a controller that decides the
  <strong>gear ratio</strong> at each simulation step so that the rover:
</p>

<ul>
  <li>Finishes the track <strong>within a time limit</strong>, and</li>
  <li>Uses <strong>minimal total energy</strong>,</li>
  <li>Without stalling or losing control.</li>
</ul>

<p>
  The <strong>physics model, track definition, and simulation loop</strong> are already implemented.
  You only implement the gear-selection logic in the controller template.
</p>

<hr>

<h2>1. Project Overview</h2>

<p>
  The simulator models a <strong>single-track bicycle rover</strong> moving along a
  <strong>1D track</strong> with varying:
</p>

<ul>
  <li><strong>Slope</strong> (uphill, flat, downhill)</li>
  <li><strong>Surface friction</strong> (good grip vs low grip)</li>
</ul>

<p>At every time-step, the simulator:</p>

<ol>
  <li>Calls your controller to obtain a <strong>gear ratio</strong> in a valid range.</li>
  <li>Computes forces and motion using the physics model.</li>
  <li>Updates position, velocity, wheel states, energy and time.</li>
  <li>
    Checks if the rover:
    <ul>
      <li>Reached the finish line (success), or</li>
      <li>Stalled on an uphill / exceeded the time limit (failure).</li>
    </ul>
  </li>
</ol>

<p>
  Your controller is a <strong>pure function</strong> that receives the current state
  and returns a gear ratio between <code>0.0</code> and <code>5.0</code>.
</p>

<hr>

<h2>2. Physics Model</h2>

<p>
  This section explains exactly how the simulator interprets your gear ratio and
  updates the vehicle state.
</p>

<h3>2.1 Vehicle Parameters</h3>

<table border="1" cellpadding="4" cellspacing="0">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Symbol</th>
      <th>Value</th>
      <th>Unit</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Total Mass</td>
      <td>m</td>
      <td>70.0</td>
      <td>kg</td>
      <td>Combined mass of rider + bicycle</td>
    </tr>
    <tr>
      <td>Wheel Radius</td>
      <td>R</td>
      <td>0.35</td>
      <td>m</td>
      <td>Radius of both wheels</td>
    </tr>
    <tr>
      <td>Wheel Moment of Inertia</td>
      <td>I</td>
      <td>0.3</td>
      <td>kg·m²</td>
      <td>Rotational inertia per wheel</td>
    </tr>
    <tr>
      <td>Input Torque</td>
      <td>T<sub>input</sub></td>
      <td>100</td>
      <td>Nm</td>
      <td>Maximum engine torque at rear wheel axle</td>
    </tr>
    <tr>
      <td>Rolling Resistance Coefficient</td>
      <td>C<sub>rr</sub></td>
      <td>0.01</td>
      <td>–</td>
      <td>Dimensionless rolling resistance coefficient</td>
    </tr>
    <tr>
      <td>Air Density</td>
      <td>ρ</td>
      <td>1.2</td>
      <td>kg/m³</td>
      <td>Standard air density</td>
    </tr>
    <tr>
      <td>Drag Coefficient</td>
      <td>C<sub>d</sub></td>
      <td>0.9</td>
      <td>–</td>
      <td>Aerodynamic drag coefficient</td>
    </tr>
    <tr>
      <td>Frontal Area</td>
      <td>A</td>
      <td>0.5</td>
      <td>m²</td>
      <td>Effective frontal area</td>
    </tr>
    <tr>
      <td>Gravity</td>
      <td>g</td>
      <td>9.81</td>
      <td>m/s²</td>
      <td>Gravitational acceleration</td>
    </tr>
  </tbody>
</table>

<h3>2.2 State Variables</h3>

<p>The main state variables used in the simulation are:</p>

<ul>
  <li><strong>Position</strong> <code>x</code> (m): distance along track from start.</li>
  <li><strong>Velocity</strong> <code>v</code> (m/s): linear forward velocity.</li>
  <li><strong>Angular velocity</strong> <code>ω</code> (rad/s): rotational speed of the driven (rear) wheel.</li>
  <li><strong>Elevation</strong> <code>h</code> (m): current height above start (derived from slope profile).</li>
  <li><strong>Time</strong> <code>t</code> (s): elapsed simulation time.</li>
  <li><strong>Energy</strong> <code>E</code> (J): total propulsion energy consumed.</li>
</ul>

<h3>2.3 Force Components</h3>

<p>
  The net longitudinal force on the bicycle is built from several components.
  The local slope is provided as a dimensionless gradient. The simulator converts
  this to an angle:
</p>

<pre><code>θ = arctan(slope)   # slope angle in radians
</code></pre>

<h4>2.3.1 Gravitational Force Along the Slope</h4>

<pre><code>F_gravity = -m * g * sin(θ)
</code></pre>

<ul>
  <li>Positive slope (uphill) ⇒ <code>sin(θ) &gt; 0</code> ⇒ <code>F_gravity</code> is negative (resists motion).</li>
  <li>Negative slope (downhill) ⇒ <code>sin(θ) &lt; 0</code> ⇒ <code>F_gravity</code> is positive (assists motion).</li>
</ul>

<h4>2.3.2 Rolling Resistance</h4>

<p>The normal force on the wheels is:</p>

<pre><code>N = m * g * cos(θ)
</code></pre>

<p>Rolling resistance is modelled as:</p>

<pre><code>ε = 1e-5  # small constant to avoid sign(0)
F_roll = -C_rr * N * sign(v + ε)
</code></pre>

<ul>
  <li>Always opposes the direction of motion.</li>
  <li>Proportional to normal force and independent of speed magnitude.</li>
</ul>

<h4>2.3.3 Aerodynamic Drag</h4>

<p>Drag increases with the square of velocity and always opposes motion:</p>

<pre><code>F_drag = -0.5 * ρ * C_d * A * v² * sign(v + ε)
</code></pre>

<ul>
  <li>At low speeds, drag is small; at high speeds, it dominates energy usage.</li>
</ul>

<h4>2.3.4 Rear Tire Traction (Magic-Formula Style)</h4>

<p>
  The tyres are modelled using a simplified longitudinal “Magic Formula” style law based on
  <strong>slip ratio</strong>.
</p>

<p>Slip ratio is computed as:</p>

<pre><code>v_safe    = max(abs(v), 0.1)        # avoid division by zero at very low speed
slip_ratio = (ω * R - v) / v_safe
</code></pre>

<ul>
  <li><code>slip_ratio &gt; 0</code> ⇒ wheel spinning faster than ground speed (driving / acceleration slip).</li>
  <li><code>slip_ratio &lt; 0</code> ⇒ wheel slower than ground speed (braking slip).</li>
  <li><code>slip_ratio = 0</code> ⇒ perfect rolling, no slip.</li>
</ul>

<p>The peak traction capacity depends on normal force and surface friction <code>μ</code>:</p>

<pre><code>D = μ * N   # peak factor (max usable longitudinal force)
B = 10.0    # stiffness factor
C = 1.9     # shape factor

F_x_rear = D * sin( C * arctan( B * slip_ratio ) )
</code></pre>

<ul>
  <li>For small slip, force roughly grows with slip ratio.</li>
  <li>Beyond a certain slip, force saturates and then may decrease ⇒ wasted torque and poor efficiency.</li>
</ul>

<h4>2.3.5 Wheel Dynamics</h4>

<h5>Rear Wheel (Driven)</h5>

<p>Given your commanded gear ratio, the applied axle torque is:</p>

<pre><code>τ = T_input * gear_ratio
</code></pre>

<p>
  The rear wheel angular acceleration is given by torque balance:
</p>

<pre><code>α_rear = (τ - F_x_rear * R) / I
</code></pre>

<ul>
  <li><code>τ</code> tries to spin the wheel faster.</li>
  <li><code>F_x_rear * R</code> is the reaction torque due to traction at the ground.</li>
</ul>

<h5>Front Wheel (Free-Rolling)</h5>

<p>
  The front wheel is not driven; it spins up due to the bike’s forward acceleration.
  Its rotational inertia adds an “effective mass” term:
</p>

<pre><code>m_eff   = m + (I / R²)        # effective mass including wheel rotation
a_bike  = F_net_static / m_eff
F_x_front = (I * a_bike) / R²
</code></pre>

<p>
  Here, <code>F_net_static</code> is the sum of all longitudinal forces
  (rear traction + gravity + rolling resistance + drag) before accounting
  for the front wheel reaction.
</p>

<h4>2.3.6 Net Longitudinal Force and Acceleration</h4>

<p>
  First, sum the main longitudinal forces excluding the front wheel reaction:
</p>

<pre><code>F_net_static = F_x_rear + F_gravity + F_roll + F_drag
</code></pre>

<p>
  Then subtract the front wheel reaction force to get the true net force on the
  bicycle body:
</p>

<pre><code>F_net = F_net_static - F_x_front
</code></pre>

<p>The resulting linear acceleration of the bike’s centre of mass is:</p>

<pre><code>a = F_net / m
</code></pre>

<p>
  The simulator then integrates <code>a</code> over time to update <code>v</code> and <code>x</code>.
</p>

<hr>

<h3>2.4 Energy Consumption Model</h3>

<p>
  Energy is only consumed when you request a positive gear ratio. Coasting is free.
</p>

<pre><code>if gear_ratio &gt; 0:
    power = max(0.0, T_input * gear_ratio * ω)   # Non-negative power at wheel
    ΔE    = power * Δt
    total_energy += ΔE
</code></pre>

<ul>
  <li><strong>Coasting</strong> (<code>gear_ratio = 0</code>) ⇒ no additional propulsion energy.</li>
  <li>
    Higher gear ratio at high angular velocity <code>ω</code> ⇒ more power ⇒ faster but
    more energy consumption.
  </li>
</ul>

<hr>

<h3>2.5 Critical Thresholds & Limits</h3>

<h4>2.5.1 Slip Threshold</h4>

<p>Slip events are counted when:</p>

<pre><code>slip_event = abs(slip_ratio) &gt; 0.15
</code></pre>

<ul>
  <li>Above ≈15% slip, traction efficiency drops significantly.</li>
  <li>Slip is allowed but wastes energy and may affect ranking (tie-breakers).</li>
</ul>

<h4>2.5.2 Gear Ratio Bounds</h4>

<p>
  The system enforces hard bounds:
</p>

<pre><code>gear_ratio_min = 0.0   # coasting (no propulsion)
gear_ratio_max = 5.0   # absolute maximum
</code></pre>

<ul>
  <li>Any value returned below 0 is clamped to 0 (coasting).</li>
  <li>Any value above 5 is clamped to 5.</li>
</ul>

<h4>2.5.3 Stalling Condition</h4>

<p>
  On uphills, the simulation detects a stall when:
</p>

<pre><code>if slope &gt; 0 and v &lt; 0.01 and F_net &lt; 0:
    failed = True   # Stalled on uphill
</code></pre>

<ul>
  <li>Very low forward speed plus net force pointing backwards ⇒ the bike cannot climb.</li>
  <li>Stall ⇒ run is marked as failed.</li>
</ul>

<h3>2.6 Time Limit</h3>

<p>
  Each track has a time limit. For the practice track, for example:
</p>

<pre><code>if total_time &gt; time_limit:   # e.g. 35 seconds
    time_limit_exceeded = True
    failed = True
</code></pre>

<ul>
  <li>If the bike does not reach the finish line within the limit, the run fails.</li>
</ul>

<hr>

<h2>3. Track &amp; Terrain Specification</h2>

<h3>3.1 Segment Definition</h3>

<p>
  The track is broken into segments, each defined as:
</p>

<pre><code>segment = (start_pos, end_pos, slope, friction_coefficient)
</code></pre>

<ul>
  <li><code>start_pos</code>, <code>end_pos</code> (m): where the segment begins and ends along the track.</li>
  <li><code>slope</code>: terrain gradient (positive = uphill, negative = downhill).</li>
  <li><code>friction_coefficient</code> (<code>μ</code>): local traction level.</li>
</ul>

<h3>3.2 Typical Terrain Types</h3>

<table border="1" cellpadding="4" cellspacing="0">
  <thead>
    <tr>
      <th>Terrain Type</th>
      <th>Slope Range</th>
      <th>Typical μ</th>
      <th>Qualitative Behaviour</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Flat</td>
      <td>-0.05 to 0.05</td>
      <td>0.7–0.8</td>
      <td>Moderate gears; maintain momentum.</td>
    </tr>
    <tr>
      <td>Gentle Uphill</td>
      <td>0.05 to 0.2</td>
      <td>0.6–0.8</td>
      <td>Need enough drive to avoid slowing too much.</td>
    </tr>
    <tr>
      <td>Steep Uphill</td>
      <td>&gt; 0.2</td>
      <td>0.5–0.8</td>
      <td>High torque demand; risk of stall and slip.</td>
    </tr>
    <tr>
      <td>Gentle Downhill</td>
      <td>-0.15 to -0.05</td>
      <td>0.4–0.8</td>
      <td>Good for coasting and momentum building.</td>
    </tr>
    <tr>
      <td>Steep Downhill</td>
      <td>&lt; -0.15</td>
      <td>0.3–0.8</td>
      <td>Coast and let gravity work; watch speed.</td>
    </tr>
    <tr>
      <td>Ice / Low Friction</td>
      <td>Any</td>
      <td>&lt; 0.5</td>
      <td>Very low grip; aggressive torque ⇒ heavy slip.</td>
    </tr>
  </tbody>
</table>

<h3>3.3 Friction Guidelines</h3>

<ul>
  <li><strong>μ ≈ 0.8</strong>: Dry asphalt (excellent traction).</li>
  <li><strong>μ ≈ 0.6</strong>: Wet asphalt (good traction).</li>
  <li><strong>μ ≈ 0.5</strong>: Gravel / loose surface (moderate traction).</li>
  <li><strong>μ ≈ 0.3</strong>: Ice (poor traction, high slip risk).</li>
</ul>

<hr>

<h2>4. Controller Interface</h2>

<h3>4.1 Function Signature</h3>

<p>
  You implement the following function in the provided template:
</p>

<pre><code>def get_gear_ratio(x: float,
                   v: float,
                   slope: float,
                   mu: float,
                   track_info: dict) -&gt; float:
    """
    Calculate the gear ratio based on current state and terrain.

    Args:
        x: Current position along track (meters).
        v: Current velocity (m/s).
        slope: Current terrain gradient (positive = uphill).
        mu: Current surface friction coefficient.
        track_info: Dictionary containing track metadata.

    Returns:
        gear_ratio: Float in range [0.0, 5.0].
    """
</code></pre>

<h3>4.2 Track Info Structure</h3>

<p><code>track_info</code> provides high-level information:</p>

<pre><code>track_info = {
    "segments": [
        (start1, end1, slope1, mu1),
        (start2, end2, slope2, mu2),
        # ...
    ],
    "next_segment": (start, end, slope, mu) or None,
    "finish_line": total_track_length
}
</code></pre>

<ul>
  <li>
    Use <code>segments</code> if you want the full profile
    (e.g. look ahead beyond the next segment).
  </li>
  <li>
    <code>next_segment</code> is a convenient way to see what is immediately ahead.
  </li>
  <li><code>finish_line</code> is the total track length in metres.</li>
</ul>

<hr>

<h2>5. Constraints, Failures, and Scoring</h2>

<h3>5.1 Qualification Requirements</h3>

<p>To be considered for ranking, a submission must:</p>

<ul>
  <li>Complete the track within the configured time limit (e.g. 35s on the practice track).</li>
  <li>Execute without runtime errors or crashes.</li>
  <li>Return valid gear ratios in the range <code>[0.0, 5.0]</code> on every call.</li>
</ul>

<h3>5.2 Failure Conditions</h3>

<ul>
  <li><strong>Time Limit Exceeded</strong>:
    <ul>
      <li>Condition: <code>total_time &gt; time_limit</code>.</li>
      <li>Effect: run is marked as failed.</li>
    </ul>
  </li>
  <li><strong>Uphill Stall</strong>:
    <ul>
      <li>Condition: <code>slope &gt; 0</code>, <code>v &lt; 0.01</code>, and <code>F_net &lt; 0</code>.</li>
      <li>Effect: run is marked as failed.</li>
    </ul>
  </li>
  <li><strong>Runtime Error</strong>:
    <ul>
      <li>Exception/crash in your controller ⇒ run failed.</li>
    </ul>
  </li>
</ul>

<h3>5.3 Slip Behaviour</h3>

<p>
  Slip events are detected when <code>abs(slip_ratio) &gt; 0.15</code> during a time-step.
  Each such time-step counts as one slip event.
</p>

<ul>
  <li>Slip does not immediately disqualify a run.</li>
  <li>Excessive slip wastes energy and may affect tie-breakers.</li>
</ul>

<h3>5.4 Scoring</h3>

<p>For each run on a test track:</p>

<ul>
  <li>If the run <strong>fails</strong>, it receives a large penalty energy (e.g. <code>1,000,000 J</code>).</li>
  <li>If the run <strong>succeeds</strong>, the run’s score is its <strong>total propulsion energy</strong> <code>E</code>.</li>
</ul>

<p>Your overall score is based on performance over multiple hidden test tracks, for example:</p>

<ul>
  <li><strong>Primary metric</strong>: average total energy over all successful runs (including penalties for failures).</li>
  <li><strong>Tie-breaker 1</strong>: lower total slip events.</li>
  <li><strong>Tie-breaker 2</strong>: lower average completion time.</li>
  <li><strong>Tie-breaker 3</strong>: lower variance in energy across runs.</li>
</ul>

<hr>

<h2>6. Strategic Considerations (Non-Binding Hints)</h2>

<p>
  You are free to design any strategy that respects the interface and constraints.
  The physics above suggests a few general ideas (these are <strong>hints</strong>, not rules):
</p>

<ul>
  <li>
    <strong>Traction preservation:</strong><br>
    The maximum usable drive force is roughly <code>F_max ≈ μ * N</code>.
    Demanding torque that would imply forces far beyond this will mainly cause slip and wasted energy.
  </li>
  <li>
    <strong>Terrain anticipation:</strong><br>
    Knowing the upcoming slope and friction through <code>track_info</code> allows you to:
    <ul>
      <li>Build momentum before steep uphills.</li>
      <li>Reduce torque before entering very low-friction regions.</li>
    </ul>
  </li>
  <li>
    <strong>Energy-conscious coasting:</strong><br>
    Since energy is only consumed when <code>gear_ratio &gt; 0</code>, coasting on downhills
    and in high-momentum states can drastically reduce energy without sacrificing time.
  </li>
  <li>
    <strong>Moderate speeds vs drag:</strong><br>
    Aerodynamic drag scales with <code>v²</code>, so extremely high speeds are usually
    energetically expensive. Moderate target speeds can be more efficient.
  </li>
  <li>
    <strong>Pulse-and-glide style behaviour:</strong><br>
    On relatively flat terrain, alternating short propulsion bursts with coasting
    can be more efficient than a constant small throttle.
  </li>
</ul>

<p>
  How you combine these ideas into an actual controller is up to you.
  The evaluation will only see your <code>get_gear_ratio</code> outputs and the resulting
  energy and completion behaviour.
</p>

<hr>

<p>
  With a solid understanding of the physics and constraints above, you should have all
  the information needed to design, implement, and iterate on your own Eco-Gear controller.
</p>

<p><strong>ALL THE BEST!</strong></p>

</body>
</html>
