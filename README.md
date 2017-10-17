# PyTracer

## Ray tracing with Python3 / PyQt5 / numpy

![alt text](test.png)

* Ray Tracing Features:
  * Geometry:
    * Sphere intersection [✓]
    * Plane intersection [✓]
    * Triangle intersection [✓]
    * Quad intersection [✓]
    * Cube intersection

  * Core:
    * Camera ray [✓]
    * Shadow ray / Direct lighting [✓]
    * Render equation integration
    * Recursive tracing [Working but slow]

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
    * Depth of field [✓]
    * Motion blur

  * Optimization:
    * Multiprocessing [✓]
    * Anti-aliasing [Need improvement]

  * Imaging:
    * Gamma correction [✓]
    * Tone mapping

* GUI Features:
  * Render window [✓]
  * Bucket render [✓]
  * Real-time update [✓]
  * Separate thread for window [✓]
  * Render time calculation [✓]
  * Interactive render
  * Global render settings [✓]
