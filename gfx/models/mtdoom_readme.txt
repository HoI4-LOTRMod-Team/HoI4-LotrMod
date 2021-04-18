In order to get the mntdoom lava to be emissive, I rewrote the PDXMesh shader to do the following:

If the diffuse texture has the value (1, 0, 1) or #ff00ff, then we mirror the y UV coordinate and output the value as emissive.

This is a SUPER dodgy way of getting emissive to work.