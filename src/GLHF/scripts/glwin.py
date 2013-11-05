from OpenGL import GLUT
from OpenGL import GLU
from OpenGL import GL

def renderScene():
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
    GL.glPushMatrix()
    # ====================
    GL.glColor(0, 1, 1)
    GL.glBegin(GL.GL_TRIANGLES)
    # -------------------------
    GL.glColor3f(1.0, 0.0, 0.0)
    GL.glVertex3f(0.0, 1.0, 0.0)
    GL.glColor3f(0.0, 1.0, 0.0)
    GL.glVertex3f(-1.0, -1.0, 0.0)
    GL.glColor3f(0.0, 0.0, 1.0)
    GL.glVertex3f(1.0, -1.0, 0.0)
    # -------------------------
    GL.glEnd()
    # ====================
    GL.glPopMatrix()
    GL.glFlush()


