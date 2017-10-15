# PyTracer

## Ray tracing with Python3 / PyQt5 / numpy

![alt text](test.png)

* Ray Tracing Features:
  * Geometry:
    * Sphere intersection [✓]
    * Plane intersection [✓]
    * Cube Intersection
    * Triangle intersection [✓]
    * Quad intersection [✓]

  * Core:
    * Camera Ray [✓]
    * Shadow Ray / Direct Lighting [✓]
    * Render Equation integration
    * Recursive tracing [Working but slow]
    * Multiprocessing [✓]

  * Light:
    * Point light [✓]
    * Area light [Disk light working]
    * Radiance unit

  * Material:
    * Diffuse / Lambert [✓]
    * Mirror [✓]
    * Glossy
    * Glass [✓]

  * Camera:
    * Camera exposure
    * Depth of field
    * Motion blur

  * Optimization:
    * multiprocessing [✓]
    * Anti-aliasing [Need improvement]

  * Imaging:
    * Gamma Correction [✓]
    * Tone mapping

* GUI Features:
  * Render Window [✓]
  * Bucket Render [Need improvement]
  * Real-time update [✓]
  * Separate thread for window [✓]
  * Render time calculation [✓]
  * Interactive Render
  * Global render settings [✓]
