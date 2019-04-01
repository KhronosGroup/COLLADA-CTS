import sys
import multiprocessing

GL_VENDOR = None
GL_RENDERER = None

def get_opengl_info(q):
    import OpenGL.GL
    import OpenGL.GLUT
    
    def __DummyDisplayFunc():
        pass
    
    OpenGL.GLUT.glutInit(sys.argv)
    # need to create a window before glGetString will return something
    OpenGL.GLUT.glutInitWindowSize(640,480)
    winId = OpenGL.GLUT.glutCreateWindow("dummy")
    OpenGL.GLUT.glutDisplayFunc(__DummyDisplayFunc)
    GL_VENDOR = OpenGL.GL.glGetString(OpenGL.GL.GL_VENDOR)
    GL_RENDERER = OpenGL.GL.glGetString(OpenGL.GL.GL_RENDERER)
    OpenGL.GLUT.glutDestroyWindow(winId)
    
    q.put((GL_VENDOR, GL_RENDERER))

if GL_VENDOR is None:
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=get_opengl_info, args=(q,))
    p.start()
    GL_VENDOR, GL_RENDERER = q.get()
    p.join()
