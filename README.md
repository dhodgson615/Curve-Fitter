# Sinusoidal Interpolation

> “Look, I’m not saying splines are *bad*. I’m just saying I’d rather divide by
> zero than drag LAPACK into yet another side project.”  
> - *me, January 11, 2025 at 1:41:17 AM, 10 seconds before making this*

Connecting scattered points smoothly is a common problem that arises in various applications, such as easing animations, shaping audio envelopes, planning a robot arm’s trajectory, or simply rendering a visually appealing curve in a plotting app. The half-period sine wave emerges as a versatile building block for this task. It never goes out outside of the range between two adjacent points, requires only two numbers per axis to define its position, is computed in linear time, behaves predictably, is perfectly smooth, and my personal favorite, it is infinitely differentiable.

---

## Why bother with half-sine interpolation?

  * A half-sine curve starts and ends with a slope of 0. By chaining several of these curves, you can create a smooth curve without any visible kinks or sudden jumps in velocity, making it ideal for simulating natural motion.

  * Because amplitude is fixed by the endpoints, the curve can’t flare out into the wild oscillations that sometimes plague polynomial fits.

  * A cubic spline segment needs four constraints and a matrix solve. A half-sine uses the endpoints alone, fits in one line of algebra, and every CPU on Earth has a hardware `sin` instruction.

  * Changing one point touches only the two adjacent segments. That locality is valuable in real-time systems and interactive editors.

---

## The Math, Step by Step

1. Given two points $P_1 = (x_1\,y_1)$ and $P_2 = (x_2\,y_2)$ with $x_2 > x_1$, we want a function $f(x)$ that  passes through both points and has zero slope at each point.

2. A shifted sine can do that:

   $f(x) = A \sin\bigl(\omega(x - \phi)\bigr) + C.$

3. Exactly half a period must fit between the x-coordinates, so $\omega = \dfrac{\pi}{x_2 - x_1}.$

4. The derivative $f'(x) = A\omega\cos(\ldots)$ vanishes when the cosine is $\pm 1$. That means the sine must start at $-\frac{\pi}{2}$ and end at $+\frac{\pi}{2}$. Translating this into a phase offset introduces a single unknown $n$.

5. **Solve for amplitude and shift**

   Plugging $x_1$ and $x_2$ into $f$ gives two linear equations:

   $A + C = y_2, \quad -A + C = y_1.$

   Adding and subtracting yields

   $A = \frac{y_2 - y_1}{2}, \qquad C = \frac{y_1 + y_2}{2}.$

6. **Collect the pieces**

   The half-sine segment finally reads

   $f(x) = \frac{y_2 - y_1}{2}\, \sin\\Bigl(\pi\,\frac{x - x_2 - n} {x_2 - x_1}\Bigr) + \frac{y_1 + y_2}{2},$

   with $n$ picked so that $f(x_1) = y_1$. The closed-form value is
   $-\frac{x_2 - x_1}{2}$, but in the code you’ll see Newton–Raphson used
   instead. That iterative form is more flexible once you start experimenting
   with non-standard easing profiles or if you need extreme precision.

---

## How the Python script ties it together

1. **`parse_coords()`**

   A quick regular expression allows you to paste points like `(1, 2), (3, 4)` directly into the console.

2. **`f()`**

   Direct transcription of the half-sine formula above.

3. **`newton_raphson()`**

   Finds the phase offset `n` by solving $f(x_1) - y_1 = 0$. Thirty iterations
   with a tight tolerance give machine-precision roots and fall back gracefully
   if the derivative ever hits zero.

4. **`interpolate()`**

   * Sort the points by `x`.

   * For each consecutive pair, compute `n`, sample 250 values of `x`, and
     store the matching `y`.

   * Append the last raw point so the plotted curve closes exactly on it.

5. **`main()`**

   Sets a dark theme, draws the interpolated curve, and overlays the original points.

---

## Extending the idea

* Use different phase angles so the derivative at $x_1$ or
  $x_2$ matches a specified value instead of 0.

* Swap the hard-coded half-period for any fraction
  you like, then keep Newton–Raphson to solve for the new phase.

* Feed the same scalars into every coordinate axis to
  bend paths in 3-D space.

---

## Caveats

* If two points share the same x-coordinate, the formula divides by 0. Skip
  or pre-process such samples.

* Every segment ends with zero velocity. If you need momentum to carry across
  points, consider quarter-cosine pairs or cubic splines.

---

## Closing thought

A half-period sine function, though conceptually small, offers significant practical advantages. It ensures continuity, predictability, and minimal computational overhead. This makes it an ideal choice for various real-world tasks, bridging the gap between straightforward linear interpolation and the more complex functionalities of full spline packages.

