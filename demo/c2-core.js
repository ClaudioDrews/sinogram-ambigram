/* Finite-grid C2 analysis. No external dependencies.
 * A half-turn is an involution R²=I wherever the finite canvas does not clip.
 * This module does not score human-readable ambigrams.
 */
(function (root) {
  "use strict";
  const GRID = 145, OFFSET = 18, CENTRE = 72.5;
  function reflectionCoordinate(index, centre) {
    return Math.round(2 * centre - 1 - index);
  }
  function rotate(source, size, centreX, centreY) {
    if (!Number.isInteger(size) || size < 1 || source.length !== size * size)
      throw new Error("Expected square raster");
    if (!Number.isFinite(centreX) || !Number.isFinite(centreY))
      throw new Error("Expected finite centre");
    const rotated = new Float64Array(source.length);
    let lost = 0;
    for (let y = 0; y < size; y++) {
      const ry = reflectionCoordinate(y, centreY);
      for (let x = 0; x < size; x++) {
        const value = source[y * size + x];
        if (!value) continue;
        const rx = reflectionCoordinate(x, centreX);
        if (rx >= 0 && rx < size && ry >= 0 && ry < size)
          rotated[ry * size + rx] = value;
        else lost += value;
      }
    }
    return { pixels: rotated, clipped: lost };
  }
  function decompose(source, size, centreX, centreY) {
    const turn = rotate(source, size, centreX, centreY);
    const even = new Float64Array(source.length);
    const odd = new Float64Array(source.length);
    let difference = 0, mass = 0, inter = 0, union = 0;
    for (let i = 0; i < source.length; i++) {
      const a = source[i], b = turn.pixels[i];
      even[i] = (a + b) / 2;
      odd[i] = (a - b) / 2;
      difference += Math.abs(a - b);
      mass += a + b;
      if (a >= .5 || b >= .5) union++;
      if (a >= .5 && b >= .5) inter++;
    }
    return {
      source, rotated: turn.pixels, even, odd, clipped: turn.clipped,
      relativeDifference: mass ? difference / mass : 0,
      binaryIoU: union ? inter / union : 1
    };
  }
  function interpolate(decomposition, t) {
    if (!Number.isFinite(t) || t < -1 || t > 1)
      throw new Error("t must be in [-1, 1]");
    const out = new Float64Array(decomposition.source.length);
    for (let i = 0; i < out.length; i++)
      out[i] = decomposition.even[i] + t * decomposition.odd[i];
    return out;
  }
  const api = {GRID, OFFSET, CENTRE, reflectionCoordinate, rotate, decompose, interpolate};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.SinogramC2Math = api;
})(typeof window === "undefined" ? globalThis : window);
