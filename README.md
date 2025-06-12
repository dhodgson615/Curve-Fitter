# Sinusoidal (Ω-Curve) Interpolation

Smoothly connecting a few scattered points is a problem that shows up
everywhere—think of easing animations, shaping audio envelopes, planning a
robot arm’s journey, or simply drawing a pretty curve through data in a
plotting app. A half-period sine wave is a surprisingly handy building block
for that job: it starts flat, ends flat, never overshoots, and needs only two
numbers per axis to pin it down.

Below you’ll find a plain-language walk-through of **why** you might pick sines
over the usual splines or high-degree polynomials, **how** the relevant
equations fall out of first-year calculus, and **what** each function in the
accompanying Python script is doing.

---

## Why bother with half-sine interpolation?

* **Visual and kinematic smoothness**

  A half sine begins and ends with zero slope. Chaining several of them yields
  a curve that has no visible kinks and no sudden jumps in velocity—perfect for
  motion that should look “natural.”

* **Predictable curvature**

  Because amplitude is fixed by the endpoints, the curve can’t flare out into
  the wild oscillations that sometimes plague polynomial fits.

* **Simplicity over splines**

  A cubic spline segment needs four constraints and a matrix solve.  A half
  sine uses the endpoints alone, fits in one line of algebra, and every CPU on
  Earth has a hardware `sin` instruction.

* **Local control**

  Changing one point touches only the two adjacent segments. That locality is
  valuable in real-time systems and interactive editors.

---

## The math, step by step

1. **Define the problem**

   Given two points $P_1 = (x_1,\,y_1), \qquad P_2 = (x_2,\,y_2) \quad
   \text{with } x_2 > x_1$, we want a function $f(x)$ that  passes through
   both points and  has zero slope at each point.

2. **Choose a model**

   A shifted sine can do that:

   $f(x) = A \sin\bigl(\omega(x - \phi)\bigr) + C.$

3. **Lock the frequency**

   Exactly half a period must fit between the x-coordinates, so $\omega =
   \dfrac{\pi}{x_2 - x_1}.$

4. **Enforce zero slopes**

   The derivative $f'(x) = A\omega\cos(\ldots)$ vanishes when the cosine is
   $\pm 1$. That means the sine must start at $-\frac{\pi}{2}$ and end at
   $+\frac{\pi}{2}$. Translating this into a phase offset introduces a single
   unknown, call it $n$.

5. **Solve for amplitude and shift**

   Plugging $x_1$ and $x_2$ into $f$ gives two linear equations:

   $A + C = y_2, \quad -A + C = y_1.$

   Adding and subtracting yields

   $A = \frac{y_2 - y_1}{2}, \qquad C = \frac{y_1 + y_2}{2}.$

6. **Collect the pieces**

   The half-sine segment finally reads  
   $ f(x) \;=\; \frac{y_2 - y_1}{2}\,
              \sin\!\Bigl(\pi\,\frac{x - x_2 - n}{x_2 - x_1}\Bigr)
            + \frac{y_1 + y_2}{2}, $  
   with $n$ picked so that $f(x_1) = y_1$. The closed-form value is $-\frac{x_2
   - x_1}{2}$, but in the code you’ll see Newton–Raphson used instead. That
   iterative form is more flexible once you start experimenting with
   non-standard easing profiles.

---

## How the Python script ties it together

1. **`parse_coords`**

   A quick regex lets you paste points like `(1, 2), (3, 4)` straight into the
   console.

2. **`f`**

   Direct transcription of the half-sine formula above.

3. **`newton_raphson`**

   Finds the phase offset `n` by solving $f(x_1) - y_1 = 0$. Thirty iterations
   with a tight tolerance give machine-precision roots and fall back gracefully
   if the derivative ever hits zero.

4. **`interpolate`**

   * Sort the points by x.

   * For each consecutive pair, compute `n`, sample 250 values of `x`, and
     store the matching `y`.

   * Append the last raw point so the plotted curve closes exactly on it.

5. **`main`**

   Sets a dark theme, draws the interpolated curve, and overlays the original
   points in red.

---

## Extending the idea

* **Custom slopes** Use different phase angles so the derivative at $x_1$ or
  $x_2$ matches a specified value instead of zero.

* **Variable easing length** Swap the hard-coded half-period for any fraction
  you like, then keep Newton–Raphson to solve for the new phase.

* **Higher dimensions** Feed the same scalars into every coordinate axis to
  bend paths in 3-D space.

---

## Caveats

* If two points share the same x-coordinate, the formula divides by zero—skip
  or pre-process such samples.

* When $y_1 = y_2$ the amplitude vanishes; you might decide a straight
  horizontal segment is clearer than a “flat” sine.

* Every segment ends with zero velocity. If you need momentum to carry across
  points, consider quarter-cosine pairs or cubic splines.

---

## Closing thought

A half-period sine is tiny in concept yet mighty in practice. It gives you
continuity, predictability, and almost no computational overhead. For many
real-world tasks that is exactly the sweet spot between raw straight-line
interpolation and the heavier machinery of full spline packages.
