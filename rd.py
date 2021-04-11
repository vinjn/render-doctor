# RenderDoc Python console, powered by python 3.6.4.
# The 'pyrenderdoc' object is the current CaptureContext instance.
# The 'renderdoc' and 'qrenderdoc' modules are available.
# Documentation is available: https://renderdoc.org/docs/python_api/index.html

# https://casual-effects.com/markdeep/features.md.html

# https://www.python.org/ftp/python/3.6.4/python-3.6.4-amd64.exe
# https://renderdoc.org/docs/python_api/renderdoc/index.html

# cpu side fetch
# C:\svn_pool\renderdoc\renderdoc\api\replay\renderdoc_replay.h
# C:\svn_pool\renderdoc\renderdoc\api\replay\data_types.h
# C:\svn_pool\renderdoc\renderdoc\api\replay\replay_enums.h

# replay the trace to get state, needs gpu
# C:\svn_pool\renderdoc\renderdoc\replay\replay_controller.h 

# TODO
# [] Add a json layer for generate_raw_data, separate raw_data and controller
# [] Add resource manager, and export to disk

import os
import sys
import math
from pathlib import Path, WindowsPath
import pprint
from datetime import datetime
from collections import defaultdict, OrderedDict
from enum import Enum, auto
import subprocess
import struct

sys.path.append('../renderdoc/x64/Development/pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('../renderdoc/x64/Development')

import renderdoc as rd

#######################################
### Config Begin
#######################################
WRITE_DETALS = False
WRITE_MALIOC = True
WRITE_CONST_BUFFER = True
WRITE_PIPELINE = True
WRITE_COLOR_BUFFER = True
WRITE_TEXTURE = True
WRITE_DEPTH_BUFFER = True
WRITE_PSO_DAG = False
#######################################
### Config End
########################################

api_full_log = None
api_short_log = None
API_TYPE = None # GraphicsAPI
IMG_EXT = 'jpg'

def getSafeName(name):
    if name[0] == '_':
        name = name[1:]
    if len(name) > 100:
        name = name[0: 99]
    return name.replace('/', '_').replace('#', '_').replace(' ', '_').replace('(', '_').replace(')', '_').replace('.', '_').replace(':', '_').replace('|', '_').replace('-', '_').replace('{', '_').replace('}', '_')

class ShaderStage(Enum):
    VS = 0
    HS = auto()
    DS = auto()
    GS = auto()
    PS = auto()
    CS = auto()

class GLChunk(Enum):
    Dummy = 0

    # C:\svn_pool\renderdoc\renderdoc\core\core.h
    DriverInit = 1
    InitialContentsList = auto()
    InitialContents = auto
    CaptureBegin = auto
    CaptureScope = auto
    CaptureEnd = 6

    FirstDriverChunk = 1000

    # C:\svn_pool\renderdoc\renderdoc\driver\gl\gl_common.h
    MakeContextCurrent = auto()
    vrapi_CreateTextureSwapChain = auto()
    vrapi_CreateTextureSwapChain2 = auto()
    glBindTexture = auto()
    glBlendFunc = auto()
    glClear = auto()
    glClearColor = auto()
    glClearDepth = auto()
    glClearStencil = auto()
    glColorMask = auto()
    glCullFace = auto()
    glDepthFunc = auto()
    glDepthMask = auto()
    glDepthRange = auto()
    glStencilFunc = auto()
    glStencilMask = auto()
    glStencilOp = auto()
    glDisable = auto()
    glDrawBuffer = auto()
    glDrawElements = auto()
    glDrawArrays = auto()
    glEnable = auto()
    glFlush = auto()
    glFinish = auto()
    glFrontFace = auto()
    glGenTextures = auto()
    glDeleteTextures = auto()
    glIsEnabled = auto()
    glIsTexture = auto()
    glGetError = auto()
    glGetTexLevelParameteriv = auto()
    glGetTexLevelParameterfv = auto()
    glGetTexParameterfv = auto()
    glGetTexParameteriv = auto()
    glGetTexImage = auto()
    glGetBooleanv = auto()
    glGetFloatv = auto()
    glGetDoublev = auto()
    glGetIntegerv = auto()
    glGetPointerv = auto()
    glGetPointervKHR = auto()
    glGetString = auto()
    glHint = auto()
    glLogicOp = auto()
    glPixelStorei = auto()
    glPixelStoref = auto()
    glPolygonMode = auto()
    glPolygonOffset = auto()
    glPointSize = auto()
    glLineWidth = auto()
    glReadPixels = auto()
    glReadBuffer = auto()
    glScissor = auto()
    glTexImage1D = auto()
    glTexImage2D = auto()
    glTexSubImage1D = auto()
    glTexSubImage2D = auto()
    glCopyTexImage1D = auto()
    glCopyTexImage2D = auto()
    glCopyTexSubImage1D = auto()
    glCopyTexSubImage2D = auto()
    glTexParameterf = auto()
    glTexParameterfv = auto()
    glTexParameteri = auto()
    glTexParameteriv = auto()
    glViewport = auto()
    glActiveTexture = auto()
    glActiveTextureARB = auto()
    glTexStorage1D = auto()
    glTexStorage1DEXT = auto()
    glTexStorage2D = auto()
    glTexStorage2DEXT = auto()
    glTexStorage3D = auto()
    glTexStorage3DEXT = auto()
    glTexStorage2DMultisample = auto()
    glTexStorage3DMultisample = auto()
    glTexStorage3DMultisampleOES = auto()
    glTexImage3D = auto()
    glTexImage3DEXT = auto()
    glTexImage3DOES = auto()
    glTexSubImage3D = auto()
    glTexSubImage3DOES = auto()
    glTexBuffer = auto()
    glTexBufferARB = auto()
    glTexBufferEXT = auto()
    glTexBufferOES = auto()
    glTexImage2DMultisample = auto()
    glTexImage3DMultisample = auto()
    glCompressedTexImage1D = auto()
    glCompressedTexImage1DARB = auto()
    glCompressedTexImage2D = auto()
    glCompressedTexImage2DARB = auto()
    glCompressedTexImage3D = auto()
    glCompressedTexImage3DARB = auto()
    glCompressedTexImage3DOES = auto()
    glCompressedTexSubImage1D = auto()
    glCompressedTexSubImage1DARB = auto()
    glCompressedTexSubImage2D = auto()
    glCompressedTexSubImage2DARB = auto()
    glCompressedTexSubImage3D = auto()
    glCompressedTexSubImage3DARB = auto()
    glCompressedTexSubImage3DOES = auto()
    glTexBufferRange = auto()
    glTexBufferRangeEXT = auto()
    glTexBufferRangeOES = auto()
    glTextureView = auto()
    glTextureViewEXT = auto()
    glTextureViewOES = auto()
    glTexParameterIiv = auto()
    glTexParameterIivEXT = auto()
    glTexParameterIivOES = auto()
    glTexParameterIuiv = auto()
    glTexParameterIuivEXT = auto()
    glTexParameterIuivOES = auto()
    glGenerateMipmap = auto()
    glGenerateMipmapEXT = auto()
    glCopyImageSubData = auto()
    glCopyImageSubDataEXT = auto()
    glCopyImageSubDataOES = auto()
    glCopyTexSubImage3D = auto()
    glCopyTexSubImage3DOES = auto()
    glGetInternalformativ = auto()
    glGetInternalformati64v = auto()
    glGetBufferParameteriv = auto()
    glGetBufferParameterivARB = auto()
    glGetBufferParameteri64v = auto()
    glGetBufferPointerv = auto()
    glGetBufferPointervARB = auto()
    glGetBufferPointervOES = auto()
    glGetFragDataIndex = auto()
    glGetFragDataLocation = auto()
    glGetFragDataLocationEXT = auto()
    glGetStringi = auto()
    glGetBooleani_v = auto()
    glGetIntegeri_v = auto()
    glGetFloati_v = auto()
    glGetFloati_vEXT = auto()
    glGetFloati_vOES = auto()
    glGetFloati_vNV = auto()
    glGetDoublei_v = auto()
    glGetDoublei_vEXT = auto()
    glGetInteger64i_v = auto()
    glGetInteger64v = auto()
    glGetShaderiv = auto()
    glGetShaderInfoLog = auto()
    glGetShaderPrecisionFormat = auto()
    glGetShaderSource = auto()
    glGetAttachedShaders = auto()
    glGetProgramiv = auto()
    glGetProgramInfoLog = auto()
    glGetProgramInterfaceiv = auto()
    glGetProgramResourceIndex = auto()
    glGetProgramResourceiv = auto()
    glGetProgramResourceName = auto()
    glGetProgramPipelineiv = auto()
    glGetProgramPipelineivEXT = auto()
    glGetProgramPipelineInfoLog = auto()
    glGetProgramPipelineInfoLogEXT = auto()
    glGetProgramBinary = auto()
    glGetProgramResourceLocation = auto()
    glGetProgramResourceLocationIndex = auto()
    glGetProgramStageiv = auto()
    glGetGraphicsResetStatus = auto()
    glGetGraphicsResetStatusARB = auto()
    glGetGraphicsResetStatusEXT = auto()
    glGetObjectLabel = auto()
    glGetObjectLabelKHR = auto()
    glGetObjectLabelEXT = auto()
    glGetObjectPtrLabel = auto()
    glGetObjectPtrLabelKHR = auto()
    glGetDebugMessageLog = auto()
    glGetDebugMessageLogARB = auto()
    glGetDebugMessageLogKHR = auto()
    glGetFramebufferAttachmentParameteriv = auto()
    glGetFramebufferAttachmentParameterivEXT = auto()
    glGetFramebufferParameteriv = auto()
    glGetRenderbufferParameteriv = auto()
    glGetRenderbufferParameterivEXT = auto()
    glGetMultisamplefv = auto()
    glGetQueryIndexediv = auto()
    glGetQueryObjectui64v = auto()
    glGetQueryObjectui64vEXT = auto()
    glGetQueryObjectuiv = auto()
    glGetQueryObjectuivARB = auto()
    glGetQueryObjectuivEXT = auto()
    glGetQueryObjecti64v = auto()
    glGetQueryObjecti64vEXT = auto()
    glGetQueryObjectiv = auto()
    glGetQueryObjectivARB = auto()
    glGetQueryObjectivEXT = auto()
    glGetQueryiv = auto()
    glGetQueryivARB = auto()
    glGetQueryivEXT = auto()
    glGetSynciv = auto()
    glGetBufferSubData = auto()
    glGetBufferSubDataARB = auto()
    glGetVertexAttribiv = auto()
    glGetVertexAttribPointerv = auto()
    glGetCompressedTexImage = auto()
    glGetCompressedTexImageARB = auto()
    glGetnCompressedTexImage = auto()
    glGetnCompressedTexImageARB = auto()
    glGetnTexImage = auto()
    glGetnTexImageARB = auto()
    glGetTexParameterIiv = auto()
    glGetTexParameterIivEXT = auto()
    glGetTexParameterIivOES = auto()
    glGetTexParameterIuiv = auto()
    glGetTexParameterIuivEXT = auto()
    glGetTexParameterIuivOES = auto()
    glClampColor = auto()
    glClampColorARB = auto()
    glReadnPixels = auto()
    glReadnPixelsARB = auto()
    glReadnPixelsEXT = auto()
    glGetSamplerParameterIiv = auto()
    glGetSamplerParameterIivEXT = auto()
    glGetSamplerParameterIivOES = auto()
    glGetSamplerParameterIuiv = auto()
    glGetSamplerParameterIuivEXT = auto()
    glGetSamplerParameterIuivOES = auto()
    glGetSamplerParameterfv = auto()
    glGetSamplerParameteriv = auto()
    glGetTransformFeedbackVarying = auto()
    glGetTransformFeedbackVaryingEXT = auto()
    glGetSubroutineIndex = auto()
    glGetSubroutineUniformLocation = auto()
    glGetActiveAtomicCounterBufferiv = auto()
    glGetActiveSubroutineName = auto()
    glGetActiveSubroutineUniformName = auto()
    glGetActiveSubroutineUniformiv = auto()
    glGetUniformLocation = auto()
    glGetUniformIndices = auto()
    glGetUniformSubroutineuiv = auto()
    glGetUniformBlockIndex = auto()
    glGetAttribLocation = auto()
    glGetActiveUniform = auto()
    glGetActiveUniformName = auto()
    glGetActiveUniformBlockName = auto()
    glGetActiveUniformBlockiv = auto()
    glGetActiveUniformsiv = auto()
    glGetActiveAttrib = auto()
    glGetUniformfv = auto()
    glGetUniformiv = auto()
    glGetUniformuiv = auto()
    glGetUniformuivEXT = auto()
    glGetUniformdv = auto()
    glGetnUniformdv = auto()
    glGetnUniformdvARB = auto()
    glGetnUniformfv = auto()
    glGetnUniformfvARB = auto()
    glGetnUniformfvEXT = auto()
    glGetnUniformiv = auto()
    glGetnUniformivARB = auto()
    glGetnUniformivEXT = auto()
    glGetnUniformuiv = auto()
    glGetnUniformuivARB = auto()
    glGetVertexAttribIiv = auto()
    glGetVertexAttribIivEXT = auto()
    glGetVertexAttribIuiv = auto()
    glGetVertexAttribIuivEXT = auto()
    glGetVertexAttribLdv = auto()
    glGetVertexAttribLdvEXT = auto()
    glGetVertexAttribdv = auto()
    glGetVertexAttribfv = auto()
    glCheckFramebufferStatus = auto()
    glCheckFramebufferStatusEXT = auto()
    glBlendColor = auto()
    glBlendColorEXT = auto()
    glBlendFunci = auto()
    glBlendFunciARB = auto()
    glBlendFunciEXT = auto()
    glBlendFunciOES = auto()
    glBlendFuncSeparate = auto()
    glBlendFuncSeparateARB = auto()
    glBlendFuncSeparatei = auto()
    glBlendFuncSeparateiARB = auto()
    glBlendFuncSeparateiEXT = auto()
    glBlendFuncSeparateiOES = auto()
    glBlendEquation = auto()
    glBlendEquationEXT = auto()
    glBlendEquationi = auto()
    glBlendEquationiARB = auto()
    glBlendEquationiEXT = auto()
    glBlendEquationiOES = auto()
    glBlendEquationSeparate = auto()
    glBlendEquationSeparateARB = auto()
    glBlendEquationSeparateEXT = auto()
    glBlendEquationSeparatei = auto()
    glBlendEquationSeparateiARB = auto()
    glBlendEquationSeparateiEXT = auto()
    glBlendEquationSeparateiOES = auto()
    glBlendBarrierKHR = auto()
    glStencilFuncSeparate = auto()
    glStencilMaskSeparate = auto()
    glStencilOpSeparate = auto()
    glColorMaski = auto()
    glColorMaskiEXT = auto()
    glColorMaskIndexedEXT = auto()
    glColorMaskiOES = auto()
    glSampleMaski = auto()
    glSampleCoverage = auto()
    glSampleCoverageARB = auto()
    glMinSampleShading = auto()
    glMinSampleShadingARB = auto()
    glMinSampleShadingOES = auto()
    glDepthRangef = auto()
    glDepthRangeIndexed = auto()
    glDepthRangeArrayv = auto()
    glClipControl = auto()
    glProvokingVertex = auto()
    glProvokingVertexEXT = auto()
    glPrimitiveRestartIndex = auto()
    glCreateShader = auto()
    glDeleteShader = auto()
    glShaderSource = auto()
    glCompileShader = auto()
    glCreateShaderProgramv = auto()
    glCreateShaderProgramvEXT = auto()
    glCreateProgram = auto()
    glDeleteProgram = auto()
    glAttachShader = auto()
    glDetachShader = auto()
    glReleaseShaderCompiler = auto()
    glLinkProgram = auto()
    glProgramParameteri = auto()
    glProgramParameteriARB = auto()
    glProgramParameteriEXT = auto()
    glUseProgram = auto()
    glShaderBinary = auto()
    glProgramBinary = auto()
    glUseProgramStages = auto()
    glUseProgramStagesEXT = auto()
    glValidateProgram = auto()
    glGenProgramPipelines = auto()
    glGenProgramPipelinesEXT = auto()
    glBindProgramPipeline = auto()
    glBindProgramPipelineEXT = auto()
    glActiveShaderProgram = auto()
    glActiveShaderProgramEXT = auto()
    glDeleteProgramPipelines = auto()
    glDeleteProgramPipelinesEXT = auto()
    glValidateProgramPipeline = auto()
    glValidateProgramPipelineEXT = auto()
    glDebugMessageCallback = auto()
    glDebugMessageCallbackARB = auto()
    glDebugMessageCallbackKHR = auto()
    glDebugMessageControl = auto()
    glDebugMessageControlARB = auto()
    glDebugMessageControlKHR = auto()
    glDebugMessageInsert = auto()
    glDebugMessageInsertARB = auto()
    glDebugMessageInsertKHR = auto()
    glPushDebugGroup = auto()
    glPushDebugGroupKHR = auto()
    glPopDebugGroup = auto()
    glPopDebugGroupKHR = auto()
    glObjectLabel = auto()
    glObjectLabelKHR = auto()
    glLabelObjectEXT = auto()
    glObjectPtrLabel = auto()
    glObjectPtrLabelKHR = auto()
    glEnablei = auto()
    glEnableiEXT = auto()
    glEnableIndexedEXT = auto()
    glEnableiOES = auto()
    glEnableiNV = auto()
    glDisablei = auto()
    glDisableiEXT = auto()
    glDisableIndexedEXT = auto()
    glDisableiOES = auto()
    glDisableiNV = auto()
    glIsEnabledi = auto()
    glIsEnablediEXT = auto()
    glIsEnabledIndexedEXT = auto()
    glIsEnablediOES = auto()
    glIsEnablediNV = auto()
    glIsBuffer = auto()
    glIsBufferARB = auto()
    glIsFramebuffer = auto()
    glIsFramebufferEXT = auto()
    glIsProgram = auto()
    glIsProgramPipeline = auto()
    glIsProgramPipelineEXT = auto()
    glIsQuery = auto()
    glIsQueryARB = auto()
    glIsQueryEXT = auto()
    glIsRenderbuffer = auto()
    glIsRenderbufferEXT = auto()
    glIsSampler = auto()
    glIsShader = auto()
    glIsSync = auto()
    glIsTransformFeedback = auto()
    glIsVertexArray = auto()
    glIsVertexArrayOES = auto()
    glGenBuffers = auto()
    glGenBuffersARB = auto()
    glBindBuffer = auto()
    glBindBufferARB = auto()
    glDrawBuffers = auto()
    glDrawBuffersARB = auto()
    glDrawBuffersEXT = auto()
    glGenFramebuffers = auto()
    glGenFramebuffersEXT = auto()
    glBindFramebuffer = auto()
    glBindFramebufferEXT = auto()
    glFramebufferTexture = auto()
    glFramebufferTextureARB = auto()
    glFramebufferTextureOES = auto()
    glFramebufferTextureEXT = auto()
    glFramebufferTexture1D = auto()
    glFramebufferTexture1DEXT = auto()
    glFramebufferTexture2D = auto()
    glFramebufferTexture2DEXT = auto()
    glFramebufferTexture3D = auto()
    glFramebufferTexture3DEXT = auto()
    glFramebufferTexture3DOES = auto()
    glFramebufferRenderbuffer = auto()
    glFramebufferRenderbufferEXT = auto()
    glFramebufferTextureLayer = auto()
    glFramebufferTextureLayerARB = auto()
    glFramebufferTextureLayerEXT = auto()
    glFramebufferParameteri = auto()
    glDeleteFramebuffers = auto()
    glDeleteFramebuffersEXT = auto()
    glGenRenderbuffers = auto()
    glGenRenderbuffersEXT = auto()
    glRenderbufferStorage = auto()
    glRenderbufferStorageEXT = auto()
    glRenderbufferStorageMultisample = auto()
    glRenderbufferStorageMultisampleEXT = auto()
    glDeleteRenderbuffers = auto()
    glDeleteRenderbuffersEXT = auto()
    glBindRenderbuffer = auto()
    glBindRenderbufferEXT = auto()
    glFenceSync = auto()
    glClientWaitSync = auto()
    glWaitSync = auto()
    glDeleteSync = auto()
    glGenQueries = auto()
    glGenQueriesARB = auto()
    glGenQueriesEXT = auto()
    glBeginQuery = auto()
    glBeginQueryARB = auto()
    glBeginQueryEXT = auto()
    glBeginQueryIndexed = auto()
    glEndQuery = auto()
    glEndQueryARB = auto()
    glEndQueryEXT = auto()
    glEndQueryIndexed = auto()
    glBeginConditionalRender = auto()
    glEndConditionalRender = auto()
    glQueryCounter = auto()
    glQueryCounterEXT = auto()
    glDeleteQueries = auto()
    glDeleteQueriesARB = auto()
    glDeleteQueriesEXT = auto()
    glBufferData = auto()
    glBufferDataARB = auto()
    glBufferStorage = auto()
    glBufferSubData = auto()
    glBufferSubDataARB = auto()
    glCopyBufferSubData = auto()
    glBindBufferBase = auto()
    glBindBufferBaseEXT = auto()
    glBindBufferRange = auto()
    glBindBufferRangeEXT = auto()
    glBindBuffersBase = auto()
    glBindBuffersRange = auto()
    glMapBuffer = auto()
    glMapBufferARB = auto()
    glMapBufferOES = auto()
    glMapBufferRange = auto()
    glFlushMappedBufferRange = auto()
    glUnmapBuffer = auto()
    glUnmapBufferARB = auto()
    glUnmapBufferOES = auto()
    glTransformFeedbackVaryings = auto()
    glTransformFeedbackVaryingsEXT = auto()
    glGenTransformFeedbacks = auto()
    glDeleteTransformFeedbacks = auto()
    glBindTransformFeedback = auto()
    glBeginTransformFeedback = auto()
    glBeginTransformFeedbackEXT = auto()
    glPauseTransformFeedback = auto()
    glResumeTransformFeedback = auto()
    glEndTransformFeedback = auto()
    glEndTransformFeedbackEXT = auto()
    glDrawTransformFeedback = auto()
    glDrawTransformFeedbackInstanced = auto()
    glDrawTransformFeedbackStream = auto()
    glDrawTransformFeedbackStreamInstanced = auto()
    glDeleteBuffers = auto()
    glDeleteBuffersARB = auto()
    glGenVertexArrays = auto()
    glGenVertexArraysOES = auto()
    glBindVertexArray = auto()
    glBindVertexArrayOES = auto()
    glDeleteVertexArrays = auto()
    glDeleteVertexArraysOES = auto()
    glVertexAttrib1d = auto()
    glVertexAttrib1dARB = auto()
    glVertexAttrib1dv = auto()
    glVertexAttrib1dvARB = auto()
    glVertexAttrib1f = auto()
    glVertexAttrib1fARB = auto()
    glVertexAttrib1fv = auto()
    glVertexAttrib1fvARB = auto()
    glVertexAttrib1s = auto()
    glVertexAttrib1sARB = auto()
    glVertexAttrib1sv = auto()
    glVertexAttrib1svARB = auto()
    glVertexAttrib2d = auto()
    glVertexAttrib2dARB = auto()
    glVertexAttrib2dv = auto()
    glVertexAttrib2dvARB = auto()
    glVertexAttrib2f = auto()
    glVertexAttrib2fARB = auto()
    glVertexAttrib2fv = auto()
    glVertexAttrib2fvARB = auto()
    glVertexAttrib2s = auto()
    glVertexAttrib2sARB = auto()
    glVertexAttrib2sv = auto()
    glVertexAttrib2svARB = auto()
    glVertexAttrib3d = auto()
    glVertexAttrib3dARB = auto()
    glVertexAttrib3dv = auto()
    glVertexAttrib3dvARB = auto()
    glVertexAttrib3f = auto()
    glVertexAttrib3fARB = auto()
    glVertexAttrib3fv = auto()
    glVertexAttrib3fvARB = auto()
    glVertexAttrib3s = auto()
    glVertexAttrib3sARB = auto()
    glVertexAttrib3sv = auto()
    glVertexAttrib3svARB = auto()
    glVertexAttrib4Nbv = auto()
    glVertexAttrib4NbvARB = auto()
    glVertexAttrib4Niv = auto()
    glVertexAttrib4NivARB = auto()
    glVertexAttrib4Nsv = auto()
    glVertexAttrib4NsvARB = auto()
    glVertexAttrib4Nub = auto()
    glVertexAttrib4Nubv = auto()
    glVertexAttrib4NubvARB = auto()
    glVertexAttrib4Nuiv = auto()
    glVertexAttrib4NuivARB = auto()
    glVertexAttrib4Nusv = auto()
    glVertexAttrib4NusvARB = auto()
    glVertexAttrib4bv = auto()
    glVertexAttrib4bvARB = auto()
    glVertexAttrib4d = auto()
    glVertexAttrib4dARB = auto()
    glVertexAttrib4dv = auto()
    glVertexAttrib4dvARB = auto()
    glVertexAttrib4f = auto()
    glVertexAttrib4fARB = auto()
    glVertexAttrib4fv = auto()
    glVertexAttrib4fvARB = auto()
    glVertexAttrib4iv = auto()
    glVertexAttrib4ivARB = auto()
    glVertexAttrib4s = auto()
    glVertexAttrib4sARB = auto()
    glVertexAttrib4sv = auto()
    glVertexAttrib4svARB = auto()
    glVertexAttrib4ubv = auto()
    glVertexAttrib4ubvARB = auto()
    glVertexAttrib4uiv = auto()
    glVertexAttrib4uivARB = auto()
    glVertexAttrib4usv = auto()
    glVertexAttrib4usvARB = auto()
    glVertexAttribI1i = auto()
    glVertexAttribI1iEXT = auto()
    glVertexAttribI1iv = auto()
    glVertexAttribI1ivEXT = auto()
    glVertexAttribI1ui = auto()
    glVertexAttribI1uiEXT = auto()
    glVertexAttribI1uiv = auto()
    glVertexAttribI1uivEXT = auto()
    glVertexAttribI2i = auto()
    glVertexAttribI2iEXT = auto()
    glVertexAttribI2iv = auto()
    glVertexAttribI2ivEXT = auto()
    glVertexAttribI2ui = auto()
    glVertexAttribI2uiEXT = auto()
    glVertexAttribI2uiv = auto()
    glVertexAttribI2uivEXT = auto()
    glVertexAttribI3i = auto()
    glVertexAttribI3iEXT = auto()
    glVertexAttribI3iv = auto()
    glVertexAttribI3ivEXT = auto()
    glVertexAttribI3ui = auto()
    glVertexAttribI3uiEXT = auto()
    glVertexAttribI3uiv = auto()
    glVertexAttribI3uivEXT = auto()
    glVertexAttribI4bv = auto()
    glVertexAttribI4bvEXT = auto()
    glVertexAttribI4i = auto()
    glVertexAttribI4iEXT = auto()
    glVertexAttribI4iv = auto()
    glVertexAttribI4ivEXT = auto()
    glVertexAttribI4sv = auto()
    glVertexAttribI4svEXT = auto()
    glVertexAttribI4ubv = auto()
    glVertexAttribI4ubvEXT = auto()
    glVertexAttribI4ui = auto()
    glVertexAttribI4uiEXT = auto()
    glVertexAttribI4uiv = auto()
    glVertexAttribI4uivEXT = auto()
    glVertexAttribI4usv = auto()
    glVertexAttribI4usvEXT = auto()
    glVertexAttribL1d = auto()
    glVertexAttribL1dEXT = auto()
    glVertexAttribL1dv = auto()
    glVertexAttribL1dvEXT = auto()
    glVertexAttribL2d = auto()
    glVertexAttribL2dEXT = auto()
    glVertexAttribL2dv = auto()
    glVertexAttribL2dvEXT = auto()
    glVertexAttribL3d = auto()
    glVertexAttribL3dEXT = auto()
    glVertexAttribL3dv = auto()
    glVertexAttribL3dvEXT = auto()
    glVertexAttribL4d = auto()
    glVertexAttribL4dEXT = auto()
    glVertexAttribL4dv = auto()
    glVertexAttribL4dvEXT = auto()
    glVertexAttribP1ui = auto()
    glVertexAttribP1uiv = auto()
    glVertexAttribP2ui = auto()
    glVertexAttribP2uiv = auto()
    glVertexAttribP3ui = auto()
    glVertexAttribP3uiv = auto()
    glVertexAttribP4ui = auto()
    glVertexAttribP4uiv = auto()
    glVertexAttribPointer = auto()
    glVertexAttribPointerARB = auto()
    glVertexAttribIPointer = auto()
    glVertexAttribIPointerEXT = auto()
    glVertexAttribLPointer = auto()
    glVertexAttribLPointerEXT = auto()
    glVertexAttribBinding = auto()
    glVertexAttribFormat = auto()
    glVertexAttribIFormat = auto()
    glVertexAttribLFormat = auto()
    glVertexAttribDivisor = auto()
    glVertexAttribDivisorARB = auto()
    glBindAttribLocation = auto()
    glBindFragDataLocation = auto()
    glBindFragDataLocationEXT = auto()
    glBindFragDataLocationIndexed = auto()
    glEnableVertexAttribArray = auto()
    glEnableVertexAttribArrayARB = auto()
    glDisableVertexAttribArray = auto()
    glDisableVertexAttribArrayARB = auto()
    glBindVertexBuffer = auto()
    glBindVertexBuffers = auto()
    glVertexBindingDivisor = auto()
    glBindImageTexture = auto()
    glBindImageTextureEXT = auto()
    glBindImageTextures = auto()
    glGenSamplers = auto()
    glBindSampler = auto()
    glBindSamplers = auto()
    glBindTextures = auto()
    glDeleteSamplers = auto()
    glSamplerParameteri = auto()
    glSamplerParameterf = auto()
    glSamplerParameteriv = auto()
    glSamplerParameterfv = auto()
    glSamplerParameterIiv = auto()
    glSamplerParameterIivEXT = auto()
    glSamplerParameterIivOES = auto()
    glSamplerParameterIuiv = auto()
    glSamplerParameterIuivEXT = auto()
    glSamplerParameterIuivOES = auto()
    glPatchParameteri = auto()
    glPatchParameteriEXT = auto()
    glPatchParameteriOES = auto()
    glPatchParameterfv = auto()
    glPointParameterf = auto()
    glPointParameterfARB = auto()
    glPointParameterfEXT = auto()
    glPointParameterfv = auto()
    glPointParameterfvARB = auto()
    glPointParameterfvEXT = auto()
    glPointParameteri = auto()
    glPointParameteriv = auto()
    glDispatchCompute = auto()
    glDispatchComputeIndirect = auto()
    glMemoryBarrier = auto()
    glMemoryBarrierEXT = auto()
    glMemoryBarrierByRegion = auto()
    glTextureBarrier = auto()
    glClearDepthf = auto()
    glClearBufferfv = auto()
    glClearBufferiv = auto()
    glClearBufferuiv = auto()
    glClearBufferfi = auto()
    glClearBufferData = auto()
    glClearBufferSubData = auto()
    glClearTexImage = auto()
    glClearTexSubImage = auto()
    glInvalidateBufferData = auto()
    glInvalidateBufferSubData = auto()
    glInvalidateFramebuffer = auto()
    glInvalidateSubFramebuffer = auto()
    glInvalidateTexImage = auto()
    glInvalidateTexSubImage = auto()
    glScissorArrayv = auto()
    glScissorArrayvOES = auto()
    glScissorArrayvNV = auto()
    glScissorIndexed = auto()
    glScissorIndexedOES = auto()
    glScissorIndexedNV = auto()
    glScissorIndexedv = auto()
    glScissorIndexedvOES = auto()
    glScissorIndexedvNV = auto()
    glViewportIndexedf = auto()
    glViewportIndexedfOES = auto()
    glViewportIndexedfNV = auto()
    glViewportIndexedfv = auto()
    glViewportIndexedfvOES = auto()
    glViewportIndexedfvNV = auto()
    glViewportArrayv = auto()
    glViewportArrayvOES = auto()
    glViewportArrayvNV = auto()
    glUniformBlockBinding = auto()
    glShaderStorageBlockBinding = auto()
    glUniformSubroutinesuiv = auto()
    glUniform1f = auto()
    glUniform1i = auto()
    glUniform1ui = auto()
    glUniform1uiEXT = auto()
    glUniform1d = auto()
    glUniform2f = auto()
    glUniform2i = auto()
    glUniform2ui = auto()
    glUniform2uiEXT = auto()
    glUniform2d = auto()
    glUniform3f = auto()
    glUniform3i = auto()
    glUniform3ui = auto()
    glUniform3uiEXT = auto()
    glUniform3d = auto()
    glUniform4f = auto()
    glUniform4i = auto()
    glUniform4ui = auto()
    glUniform4uiEXT = auto()
    glUniform4d = auto()
    glUniform1fv = auto()
    glUniform1iv = auto()
    glUniform1uiv = auto()
    glUniform1uivEXT = auto()
    glUniform1dv = auto()
    glUniform2fv = auto()
    glUniform2iv = auto()
    glUniform2uiv = auto()
    glUniform2uivEXT = auto()
    glUniform2dv = auto()
    glUniform3fv = auto()
    glUniform3iv = auto()
    glUniform3uiv = auto()
    glUniform3uivEXT = auto()
    glUniform3dv = auto()
    glUniform4fv = auto()
    glUniform4iv = auto()
    glUniform4uiv = auto()
    glUniform4uivEXT = auto()
    glUniform4dv = auto()
    glUniformMatrix2fv = auto()
    glUniformMatrix2x3fv = auto()
    glUniformMatrix2x4fv = auto()
    glUniformMatrix3fv = auto()
    glUniformMatrix3x2fv = auto()
    glUniformMatrix3x4fv = auto()
    glUniformMatrix4fv = auto()
    glUniformMatrix4x2fv = auto()
    glUniformMatrix4x3fv = auto()
    glUniformMatrix2dv = auto()
    glUniformMatrix2x3dv = auto()
    glUniformMatrix2x4dv = auto()
    glUniformMatrix3dv = auto()
    glUniformMatrix3x2dv = auto()
    glUniformMatrix3x4dv = auto()
    glUniformMatrix4dv = auto()
    glUniformMatrix4x2dv = auto()
    glUniformMatrix4x3dv = auto()
    glProgramUniform1f = auto()
    glProgramUniform1fEXT = auto()
    glProgramUniform1i = auto()
    glProgramUniform1iEXT = auto()
    glProgramUniform1ui = auto()
    glProgramUniform1uiEXT = auto()
    glProgramUniform1d = auto()
    glProgramUniform1dEXT = auto()
    glProgramUniform2f = auto()
    glProgramUniform2fEXT = auto()
    glProgramUniform2i = auto()
    glProgramUniform2iEXT = auto()
    glProgramUniform2ui = auto()
    glProgramUniform2uiEXT = auto()
    glProgramUniform2d = auto()
    glProgramUniform2dEXT = auto()
    glProgramUniform3f = auto()
    glProgramUniform3fEXT = auto()
    glProgramUniform3i = auto()
    glProgramUniform3iEXT = auto()
    glProgramUniform3ui = auto()
    glProgramUniform3uiEXT = auto()
    glProgramUniform3d = auto()
    glProgramUniform3dEXT = auto()
    glProgramUniform4f = auto()
    glProgramUniform4fEXT = auto()
    glProgramUniform4i = auto()
    glProgramUniform4iEXT = auto()
    glProgramUniform4ui = auto()
    glProgramUniform4uiEXT = auto()
    glProgramUniform4d = auto()
    glProgramUniform4dEXT = auto()
    glProgramUniform1fv = auto()
    glProgramUniform1fvEXT = auto()
    glProgramUniform1iv = auto()
    glProgramUniform1ivEXT = auto()
    glProgramUniform1uiv = auto()
    glProgramUniform1uivEXT = auto()
    glProgramUniform1dv = auto()
    glProgramUniform1dvEXT = auto()
    glProgramUniform2fv = auto()
    glProgramUniform2fvEXT = auto()
    glProgramUniform2iv = auto()
    glProgramUniform2ivEXT = auto()
    glProgramUniform2uiv = auto()
    glProgramUniform2uivEXT = auto()
    glProgramUniform2dv = auto()
    glProgramUniform2dvEXT = auto()
    glProgramUniform3fv = auto()
    glProgramUniform3fvEXT = auto()
    glProgramUniform3iv = auto()
    glProgramUniform3ivEXT = auto()
    glProgramUniform3uiv = auto()
    glProgramUniform3uivEXT = auto()
    glProgramUniform3dv = auto()
    glProgramUniform3dvEXT = auto()
    glProgramUniform4fv = auto()
    glProgramUniform4fvEXT = auto()
    glProgramUniform4iv = auto()
    glProgramUniform4ivEXT = auto()
    glProgramUniform4uiv = auto()
    glProgramUniform4uivEXT = auto()
    glProgramUniform4dv = auto()
    glProgramUniform4dvEXT = auto()
    glProgramUniformMatrix2fv = auto()
    glProgramUniformMatrix2fvEXT = auto()
    glProgramUniformMatrix2x3fv = auto()
    glProgramUniformMatrix2x3fvEXT = auto()
    glProgramUniformMatrix2x4fv = auto()
    glProgramUniformMatrix2x4fvEXT = auto()
    glProgramUniformMatrix3fv = auto()
    glProgramUniformMatrix3fvEXT = auto()
    glProgramUniformMatrix3x2fv = auto()
    glProgramUniformMatrix3x2fvEXT = auto()
    glProgramUniformMatrix3x4fv = auto()
    glProgramUniformMatrix3x4fvEXT = auto()
    glProgramUniformMatrix4fv = auto()
    glProgramUniformMatrix4fvEXT = auto()
    glProgramUniformMatrix4x2fv = auto()
    glProgramUniformMatrix4x2fvEXT = auto()
    glProgramUniformMatrix4x3fv = auto()
    glProgramUniformMatrix4x3fvEXT = auto()
    glProgramUniformMatrix2dv = auto()
    glProgramUniformMatrix2dvEXT = auto()
    glProgramUniformMatrix2x3dv = auto()
    glProgramUniformMatrix2x3dvEXT = auto()
    glProgramUniformMatrix2x4dv = auto()
    glProgramUniformMatrix2x4dvEXT = auto()
    glProgramUniformMatrix3dv = auto()
    glProgramUniformMatrix3dvEXT = auto()
    glProgramUniformMatrix3x2dv = auto()
    glProgramUniformMatrix3x2dvEXT = auto()
    glProgramUniformMatrix3x4dv = auto()
    glProgramUniformMatrix3x4dvEXT = auto()
    glProgramUniformMatrix4dv = auto()
    glProgramUniformMatrix4dvEXT = auto()
    glProgramUniformMatrix4x2dv = auto()
    glProgramUniformMatrix4x2dvEXT = auto()
    glProgramUniformMatrix4x3dv = auto()
    glProgramUniformMatrix4x3dvEXT = auto()
    glDrawRangeElements = auto()
    glDrawRangeElementsEXT = auto()
    glDrawRangeElementsBaseVertex = auto()
    glDrawRangeElementsBaseVertexEXT = auto()
    glDrawRangeElementsBaseVertexOES = auto()
    glDrawArraysInstancedBaseInstance = auto()
    glDrawArraysInstancedBaseInstanceEXT = auto()
    glDrawArraysInstanced = auto()
    glDrawArraysInstancedARB = auto()
    glDrawArraysInstancedEXT = auto()
    glDrawElementsInstanced = auto()
    glDrawElementsInstancedARB = auto()
    glDrawElementsInstancedEXT = auto()
    glDrawElementsInstancedBaseInstance = auto()
    glDrawElementsInstancedBaseInstanceEXT = auto()
    glDrawElementsBaseVertex = auto()
    glDrawElementsBaseVertexEXT = auto()
    glDrawElementsBaseVertexOES = auto()
    glDrawElementsInstancedBaseVertex = auto()
    glDrawElementsInstancedBaseVertexEXT = auto()
    glDrawElementsInstancedBaseVertexOES = auto()
    glDrawElementsInstancedBaseVertexBaseInstance = auto()
    glDrawElementsInstancedBaseVertexBaseInstanceEXT = auto()
    glMultiDrawArrays = auto()
    glMultiDrawArraysEXT = auto()
    glMultiDrawElements = auto()
    glMultiDrawElementsBaseVertex = auto()
    glMultiDrawElementsBaseVertexEXT = auto()
    glMultiDrawElementsBaseVertexOES = auto()
    glMultiDrawArraysIndirect = auto()
    glMultiDrawElementsIndirect = auto()
    glDrawArraysIndirect = auto()
    glDrawElementsIndirect = auto()
    glBlitFramebuffer = auto()
    glBlitFramebufferEXT = auto()
    glPrimitiveBoundingBox = auto()
    glPrimitiveBoundingBoxEXT = auto()
    glPrimitiveBoundingBoxOES = auto()
    glBlendBarrier = auto()
    glFramebufferTexture2DMultisampleEXT = auto()
    glDiscardFramebufferEXT = auto()
    glDepthRangeArrayfvOES = auto()
    glDepthRangeArrayfvNV = auto()
    glDepthRangeIndexedfOES = auto()
    glDepthRangeIndexedfNV = auto()
    glNamedStringARB = auto()
    glDeleteNamedStringARB = auto()
    glCompileShaderIncludeARB = auto()
    glIsNamedStringARB = auto()
    glGetNamedStringARB = auto()
    glGetNamedStringivARB = auto()
    glDispatchComputeGroupSizeARB = auto()
    glMultiDrawArraysIndirectCountARB = auto()
    glMultiDrawElementsIndirectCountARB = auto()
    glRasterSamplesEXT = auto()
    glDepthBoundsEXT = auto()
    glPolygonOffsetClampEXT = auto()
    glInsertEventMarkerEXT = auto()
    glPushGroupMarkerEXT = auto()
    glPopGroupMarkerEXT = auto()
    glFrameTerminatorGREMEDY = auto()
    glStringMarkerGREMEDY = auto()
    glFramebufferTextureMultiviewOVR = auto()
    glFramebufferTextureMultisampleMultiviewOVR = auto()
    glCompressedTextureImage1DEXT = auto()
    glCompressedTextureImage2DEXT = auto()
    glCompressedTextureImage3DEXT = auto()
    glCompressedTextureSubImage1DEXT = auto()
    glCompressedTextureSubImage2DEXT = auto()
    glCompressedTextureSubImage3DEXT = auto()
    glGenerateTextureMipmapEXT = auto()
    glGetPointeri_vEXT = auto()
    glGetDoubleIndexedvEXT = auto()
    glGetPointerIndexedvEXT = auto()
    glGetIntegerIndexedvEXT = auto()
    glGetBooleanIndexedvEXT = auto()
    glGetFloatIndexedvEXT = auto()
    glGetMultiTexImageEXT = auto()
    glGetMultiTexParameterfvEXT = auto()
    glGetMultiTexParameterivEXT = auto()
    glGetMultiTexParameterIivEXT = auto()
    glGetMultiTexParameterIuivEXT = auto()
    glGetMultiTexLevelParameterfvEXT = auto()
    glGetMultiTexLevelParameterivEXT = auto()
    glGetCompressedMultiTexImageEXT = auto()
    glGetNamedBufferPointervEXT = auto()
    glGetNamedBufferPointerv = auto()
    glGetNamedProgramivEXT = auto()
    glGetNamedFramebufferAttachmentParameterivEXT = auto()
    glGetNamedFramebufferAttachmentParameteriv = auto()
    glGetNamedBufferParameterivEXT = auto()
    glGetNamedBufferParameteriv = auto()
    glCheckNamedFramebufferStatusEXT = auto()
    glCheckNamedFramebufferStatus = auto()
    glGetNamedBufferSubDataEXT = auto()
    glGetNamedFramebufferParameterivEXT = auto()
    glGetFramebufferParameterivEXT = auto()
    glGetNamedFramebufferParameteriv = auto()
    glGetNamedRenderbufferParameterivEXT = auto()
    glGetNamedRenderbufferParameteriv = auto()
    glGetVertexArrayIntegervEXT = auto()
    glGetVertexArrayPointervEXT = auto()
    glGetVertexArrayIntegeri_vEXT = auto()
    glGetVertexArrayPointeri_vEXT = auto()
    glGetCompressedTextureImageEXT = auto()
    glGetTextureImageEXT = auto()
    glGetTextureParameterivEXT = auto()
    glGetTextureParameterfvEXT = auto()
    glGetTextureParameterIivEXT = auto()
    glGetTextureParameterIuivEXT = auto()
    glGetTextureLevelParameterivEXT = auto()
    glGetTextureLevelParameterfvEXT = auto()
    glBindMultiTextureEXT = auto()
    glMapNamedBufferEXT = auto()
    glMapNamedBuffer = auto()
    glMapNamedBufferRangeEXT = auto()
    glFlushMappedNamedBufferRangeEXT = auto()
    glUnmapNamedBufferEXT = auto()
    glUnmapNamedBuffer = auto()
    glClearNamedBufferDataEXT = auto()
    glClearNamedBufferData = auto()
    glClearNamedBufferSubDataEXT = auto()
    glNamedBufferDataEXT = auto()
    glNamedBufferStorageEXT = auto()
    glNamedBufferSubDataEXT = auto()
    glNamedCopyBufferSubDataEXT = auto()
    glNamedFramebufferTextureEXT = auto()
    glNamedFramebufferTexture = auto()
    glNamedFramebufferTexture1DEXT = auto()
    glNamedFramebufferTexture2DEXT = auto()
    glNamedFramebufferTexture3DEXT = auto()
    glNamedFramebufferRenderbufferEXT = auto()
    glNamedFramebufferRenderbuffer = auto()
    glNamedFramebufferTextureLayerEXT = auto()
    glNamedFramebufferTextureLayer = auto()
    glNamedFramebufferParameteriEXT = auto()
    glNamedFramebufferParameteri = auto()
    glNamedRenderbufferStorageEXT = auto()
    glNamedRenderbufferStorage = auto()
    glNamedRenderbufferStorageMultisampleEXT = auto()
    glNamedRenderbufferStorageMultisample = auto()
    glFramebufferDrawBufferEXT = auto()
    glNamedFramebufferDrawBuffer = auto()
    glFramebufferDrawBuffersEXT = auto()
    glNamedFramebufferDrawBuffers = auto()
    glFramebufferReadBufferEXT = auto()
    glNamedFramebufferReadBuffer = auto()
    glTextureBufferEXT = auto()
    glTextureBufferRangeEXT = auto()
    glTextureImage1DEXT = auto()
    glTextureImage2DEXT = auto()
    glTextureImage3DEXT = auto()
    glTextureParameterfEXT = auto()
    glTextureParameterfvEXT = auto()
    glTextureParameteriEXT = auto()
    glTextureParameterivEXT = auto()
    glTextureParameterIivEXT = auto()
    glTextureParameterIuivEXT = auto()
    glTextureStorage1DEXT = auto()
    glTextureStorage2DEXT = auto()
    glTextureStorage3DEXT = auto()
    glTextureStorage2DMultisampleEXT = auto()
    glTextureStorage3DMultisampleEXT = auto()
    glTextureSubImage1DEXT = auto()
    glTextureSubImage2DEXT = auto()
    glTextureSubImage3DEXT = auto()
    glCopyTextureImage1DEXT = auto()
    glCopyTextureImage2DEXT = auto()
    glCopyTextureSubImage1DEXT = auto()
    glCopyTextureSubImage2DEXT = auto()
    glCopyTextureSubImage3DEXT = auto()
    glMultiTexParameteriEXT = auto()
    glMultiTexParameterivEXT = auto()
    glMultiTexParameterfEXT = auto()
    glMultiTexParameterfvEXT = auto()
    glMultiTexImage1DEXT = auto()
    glMultiTexImage2DEXT = auto()
    glMultiTexSubImage1DEXT = auto()
    glMultiTexSubImage2DEXT = auto()
    glCopyMultiTexImage1DEXT = auto()
    glCopyMultiTexImage2DEXT = auto()
    glCopyMultiTexSubImage1DEXT = auto()
    glCopyMultiTexSubImage2DEXT = auto()
    glMultiTexImage3DEXT = auto()
    glMultiTexSubImage3DEXT = auto()
    glCopyMultiTexSubImage3DEXT = auto()
    glCompressedMultiTexImage3DEXT = auto()
    glCompressedMultiTexImage2DEXT = auto()
    glCompressedMultiTexImage1DEXT = auto()
    glCompressedMultiTexSubImage3DEXT = auto()
    glCompressedMultiTexSubImage2DEXT = auto()
    glCompressedMultiTexSubImage1DEXT = auto()
    glMultiTexBufferEXT = auto()
    glMultiTexParameterIivEXT = auto()
    glMultiTexParameterIuivEXT = auto()
    glGenerateMultiTexMipmapEXT = auto()
    glVertexArrayVertexAttribOffsetEXT = auto()
    glVertexArrayVertexAttribIOffsetEXT = auto()
    glEnableVertexArrayAttribEXT = auto()
    glEnableVertexArrayAttrib = auto()
    glDisableVertexArrayAttribEXT = auto()
    glDisableVertexArrayAttrib = auto()
    glVertexArrayBindVertexBufferEXT = auto()
    glVertexArrayVertexBuffer = auto()
    glVertexArrayVertexAttribFormatEXT = auto()
    glVertexArrayAttribFormat = auto()
    glVertexArrayVertexAttribIFormatEXT = auto()
    glVertexArrayAttribIFormat = auto()
    glVertexArrayVertexAttribLFormatEXT = auto()
    glVertexArrayAttribLFormat = auto()
    glVertexArrayVertexAttribBindingEXT = auto()
    glVertexArrayAttribBinding = auto()
    glVertexArrayVertexBindingDivisorEXT = auto()
    glVertexArrayBindingDivisor = auto()
    glVertexArrayVertexAttribLOffsetEXT = auto()
    glVertexArrayVertexAttribDivisorEXT = auto()
    glCreateTransformFeedbacks = auto()
    glTransformFeedbackBufferBase = auto()
    glTransformFeedbackBufferRange = auto()
    glGetTransformFeedbacki64_v = auto()
    glGetTransformFeedbacki_v = auto()
    glGetTransformFeedbackiv = auto()
    glCreateBuffers = auto()
    glGetNamedBufferSubData = auto()
    glNamedBufferStorage = auto()
    glNamedBufferData = auto()
    glNamedBufferSubData = auto()
    glCopyNamedBufferSubData = auto()
    glClearNamedBufferSubData = auto()
    glMapNamedBufferRange = auto()
    glFlushMappedNamedBufferRange = auto()
    glGetNamedBufferParameteri64v = auto()
    glCreateFramebuffers = auto()
    glInvalidateNamedFramebufferData = auto()
    glInvalidateNamedFramebufferSubData = auto()
    glClearNamedFramebufferiv = auto()
    glClearNamedFramebufferuiv = auto()
    glClearNamedFramebufferfv = auto()
    glClearNamedFramebufferfi = auto()
    glBlitNamedFramebuffer = auto()
    glCreateRenderbuffers = auto()
    glCreateTextures = auto()
    glTextureBuffer = auto()
    glTextureBufferRange = auto()
    glTextureStorage1D = auto()
    glTextureStorage2D = auto()
    glTextureStorage3D = auto()
    glTextureStorage2DMultisample = auto()
    glTextureStorage3DMultisample = auto()
    glTextureSubImage1D = auto()
    glTextureSubImage2D = auto()
    glTextureSubImage3D = auto()
    glCompressedTextureSubImage1D = auto()
    glCompressedTextureSubImage2D = auto()
    glCompressedTextureSubImage3D = auto()
    glCopyTextureSubImage1D = auto()
    glCopyTextureSubImage2D = auto()
    glCopyTextureSubImage3D = auto()
    glTextureParameterf = auto()
    glTextureParameterfv = auto()
    glTextureParameteri = auto()
    glTextureParameterIiv = auto()
    glTextureParameterIuiv = auto()
    glTextureParameteriv = auto()
    glGenerateTextureMipmap = auto()
    glBindTextureUnit = auto()
    glGetTextureImage = auto()
    glGetTextureSubImage = auto()
    glGetCompressedTextureImage = auto()
    glGetCompressedTextureSubImage = auto()
    glGetTextureLevelParameterfv = auto()
    glGetTextureLevelParameteriv = auto()
    glGetTextureParameterIiv = auto()
    glGetTextureParameterIuiv = auto()
    glGetTextureParameterfv = auto()
    glGetTextureParameteriv = auto()
    glCreateVertexArrays = auto()
    glCreateSamplers = auto()
    glCreateProgramPipelines = auto()
    glCreateQueries = auto()
    glVertexArrayElementBuffer = auto()
    glVertexArrayVertexBuffers = auto()
    glGetVertexArrayiv = auto()
    glGetVertexArrayIndexed64iv = auto()
    glGetVertexArrayIndexediv = auto()
    glGetQueryBufferObjecti64v = auto()
    glGetQueryBufferObjectiv = auto()
    glGetQueryBufferObjectui64v = auto()
    glGetQueryBufferObjectuiv = auto()
    wglDXSetResourceShareHandleNV = auto()
    wglDXOpenDeviceNV = auto()
    wglDXCloseDeviceNV = auto()
    wglDXRegisterObjectNV = auto()
    wglDXUnregisterObjectNV = auto()
    wglDXObjectAccessNV = auto()
    wglDXLockObjectsNV = auto()
    wglDXUnlockObjectsNV = auto()

    glIndirectSubCommand = auto()

    glContextInit = auto()

    glMultiDrawArraysIndirectCount = auto()
    glMultiDrawElementsIndirectCount = auto()
    glPolygonOffsetClamp = auto()
    glMaxShaderCompilerThreadsARB = auto()
    glMaxShaderCompilerThreadsKHR = auto()

    glSpecializeShader = auto()
    glSpecializeShaderARB = auto()

    glUniform1fARB = auto()
    glUniform1iARB = auto()
    glUniform2fARB = auto()
    glUniform2iARB = auto()
    glUniform3fARB = auto()
    glUniform3iARB = auto()
    glUniform4fARB = auto()
    glUniform4iARB = auto()
    glUniform1fvARB = auto()
    glUniform1ivARB = auto()
    glUniform2fvARB = auto()
    glUniform2ivARB = auto()
    glUniform3fvARB = auto()
    glUniform3ivARB = auto()
    glUniform4fvARB = auto()
    glUniform4ivARB = auto()
    glUniformMatrix2fvARB = auto()
    glUniformMatrix3fvARB = auto()
    glUniformMatrix4fvARB = auto()

    glGetUnsignedBytevEXT = auto()
    glGetUnsignedBytei_vEXT = auto()
    glDeleteMemoryObjectsEXT = auto()
    glIsMemoryObjectEXT = auto()
    glCreateMemoryObjectsEXT = auto()
    glMemoryObjectParameterivEXT = auto()
    glGetMemoryObjectParameterivEXT = auto()
    glTexStorageMem2DEXT = auto()
    glTexStorageMem2DMultisampleEXT = auto()
    glTexStorageMem3DEXT = auto()
    glTexStorageMem3DMultisampleEXT = auto()
    glBufferStorageMemEXT = auto()
    glTextureStorageMem2DEXT = auto()
    glTextureStorageMem2DMultisampleEXT = auto()
    glTextureStorageMem3DEXT = auto()
    glTextureStorageMem3DMultisampleEXT = auto()
    glNamedBufferStorageMemEXT = auto()
    glTexStorageMem1DEXT = auto()
    glTextureStorageMem1DEXT = auto()
    glGenSemaphoresEXT = auto()
    glDeleteSemaphoresEXT = auto()
    glIsSemaphoreEXT = auto()
    glSemaphoreParameterui64vEXT = auto()
    glGetSemaphoreParameterui64vEXT = auto()
    glWaitSemaphoreEXT = auto()
    glSignalSemaphoreEXT = auto()
    glImportMemoryFdEXT = auto()
    glImportSemaphoreFdEXT = auto()
    glImportMemoryWin32HandleEXT = auto()
    glImportMemoryWin32NameEXT = auto()
    glImportSemaphoreWin32HandleEXT = auto()
    glImportSemaphoreWin32NameEXT = auto()
    glAcquireKeyedMutexWin32EXT = auto()
    glReleaseKeyedMutexWin32EXT = auto()

    ContextConfiguration = auto()

    glTextureFoveationParametersQCOM = auto()

    glBufferStorageEXT = auto()

    CoherentMapWrite = auto()

    glBeginPerfQueryINTEL = auto()
    glCreatePerfQueryINTEL = auto()
    glDeletePerfQueryINTEL = auto()
    glEndPerfQueryINTEL = auto()
    glGetFirstPerfQueryIdINTEL = auto()
    glGetNextPerfQueryIdINTEL = auto()
    glGetPerfCounterInfoINTEL = auto()
    glGetPerfQueryDataINTEL = auto()
    glGetPerfQueryIdByNameINTEL = auto()
    glGetPerfQueryInfoINTEL = auto()

    glBlendEquationARB = auto()
    glPrimitiveBoundingBoxARB = auto()

    SwapBuffers = auto()
    wglSwapBuffers = auto()
    glXSwapBuffers = auto()
    CGLFlushDrawable = auto()
    eglSwapBuffers = auto()
    eglPostSubBufferNV = auto()
    eglSwapBuffersWithDamageEXT = auto()
    eglSwapBuffersWithDamageKHR = auto()

    ImplicitThreadSwitch = auto()

    Count = auto()


class D3D11Chunk(Enum):
    Dummy = 0

    # C:\svn_pool\renderdoc\renderdoc\core\core.h
    DriverInit = 1
    InitialContentsList = auto()
    InitialContents = auto()
    CaptureBegin = auto()
    CaptureScope = auto()
    CaptureEnd = auto()

    FirstDriverChunk = 1000

    SetResourceName = auto()
    CreateSwapBuffer = auto()
    CreateTexture1D = auto()
    CreateTexture2D = auto()
    CreateTexture3D = auto()
    CreateBuffer = auto()
    CreateVertexShader = auto()
    CreateHullShader = auto()
    CreateDomainShader = auto()
    CreateGeometryShader = auto()
    CreateGeometryShaderWithStreamOutput = auto()
    CreatePixelShader = auto()
    CreateComputeShader = auto()
    GetClassInstance = auto()
    CreateClassInstance = auto()
    CreateClassLinkage = auto()
    CreateShaderResourceView = auto()
    CreateRenderTargetView = auto()
    CreateDepthStencilView = auto()
    CreateUnorderedAccessView = auto()
    CreateInputLayout = auto()
    CreateBlendState = auto()
    CreateDepthStencilState = auto()
    CreateRasterizerState = auto()
    CreateSamplerState = auto()
    CreateQuery = auto()
    CreatePredicate = auto()
    CreateCounter = auto()
    CreateDeferredContext = auto()
    SetExceptionMode = auto()
    OpenSharedResource = auto()
    IASetInputLayout = auto()
    IASetVertexBuffers = auto()
    IASetIndexBuffer = auto()
    IASetPrimitiveTopology = auto()
    VSSetConstantBuffers = auto()
    VSSetShaderResources = auto()
    VSSetSamplers = auto()
    VSSetShader = auto()
    HSSetConstantBuffers = auto()
    HSSetShaderResources = auto()
    HSSetSamplers = auto()
    HSSetShader = auto()
    DSSetConstantBuffers = auto()
    DSSetShaderResources = auto()
    DSSetSamplers = auto()
    DSSetShader = auto()
    GSSetConstantBuffers = auto()
    GSSetShaderResources = auto()
    GSSetSamplers = auto()
    GSSetShader = auto()
    SOSetTargets = auto()
    PSSetConstantBuffers = auto()
    PSSetShaderResources = auto()
    PSSetSamplers = auto()
    PSSetShader = auto()
    CSSetConstantBuffers = auto()
    CSSetShaderResources = auto()
    CSSetUnorderedAccessViews = auto()
    CSSetSamplers = auto()
    CSSetShader = auto()
    RSSetViewports = auto()
    RSSetScissorRects = auto()
    RSSetState = auto()
    OMSetRenderTargets = auto()
    OMSetRenderTargetsAndUnorderedAccessViews = auto()
    OMSetBlendState = auto()
    OMSetDepthStencilState = auto()
    DrawIndexedInstanced = auto()
    DrawInstanced = auto()
    DrawIndexed = auto()
    Draw = auto()
    DrawAuto = auto()
    DrawIndexedInstancedIndirect = auto()
    DrawInstancedIndirect = auto()
    Map = auto()
    Unmap = auto()
    CopySubresourceRegion = auto()
    CopyResource = auto()
    UpdateSubresource = auto()
    CopyStructureCount = auto()
    ResolveSubresource = auto()
    GenerateMips = auto()
    ClearDepthStencilView = auto()
    ClearRenderTargetView = auto()
    ClearUnorderedAccessViewUint = auto()
    ClearUnorderedAccessViewFloat = auto()
    ClearState = auto()
    ExecuteCommandList = auto()
    Dispatch = auto()
    DispatchIndirect = auto()
    FinishCommandList = auto()
    Flush = auto()
    SetPredication = auto()
    SetResourceMinLOD = auto()
    Begin = auto()
    End = auto()
    CreateRasterizerState1 = auto()
    CreateBlendState1 = auto()
    CopySubresourceRegion1 = auto()
    UpdateSubresource1 = auto()
    ClearView = auto()
    VSSetConstantBuffers1 = auto()
    HSSetConstantBuffers1 = auto()
    DSSetConstantBuffers1 = auto()
    GSSetConstantBuffers1 = auto()
    PSSetConstantBuffers1 = auto()
    CSSetConstantBuffers1 = auto()
    PushMarker = auto()
    SetMarker = auto()
    PopMarker = auto()
    SetShaderDebugPath = auto()
    DiscardResource = auto()
    DiscardView = auto()
    DiscardView1 = auto()
    CreateRasterizerState2 = auto()
    CreateQuery1 = auto()
    CreateTexture2D1 = auto()
    CreateTexture3D1 = auto()
    CreateShaderResourceView1 = auto()
    CreateRenderTargetView1 = auto()
    CreateUnorderedAccessView1 = auto()
    SwapchainPresent = auto()
    PostExecuteCommandList = auto()
    PostFinishCommandListSet = auto()
    SwapDeviceContextState = auto()
    ExternalDXGIResource = auto()
    OpenSharedResource1 = auto()
    OpenSharedResourceByName = auto()
    
    Count = auto()

class VulkanChunk(Enum):
    Dummy = 0

    # C:\svn_pool\renderdoc\renderdoc\core\core.h
    DriverInit = 1
    InitialContentsList = auto()
    InitialContents = auto()
    CaptureBegin = auto()
    CaptureScope = auto()
    CaptureEnd = auto()

    FirstDriverChunk = 1000

    vkCreateDevice = auto()
    vkGetDeviceQueue = auto()
    vkAllocateMemory = auto()
    vkUnmapMemory = auto()
    vkFlushMappedMemoryRanges = auto()
    vkCreateCommandPool = auto()
    vkResetCommandPool = auto()
    vkAllocateCommandBuffers = auto()
    vkCreateFramebuffer = auto()
    vkCreateRenderPass = auto()
    vkCreateDescriptorPool = auto()
    vkCreateDescriptorSetLayout = auto()
    vkCreateBuffer = auto()
    vkCreateBufferView = auto()
    vkCreateImage = auto()
    vkCreateImageView = auto()
    vkCreateDepthTargetView = auto()
    vkCreateSampler = auto()
    vkCreateShaderModule = auto()
    vkCreatePipelineLayout = auto()
    vkCreatePipelineCache = auto()
    vkCreateGraphicsPipelines = auto()
    vkCreateComputePipelines = auto()
    vkGetSwapchainImagesKHR = auto()
    vkCreateSemaphore = auto()
    vkCreateFence = auto()
    vkGetFenceStatus = auto()
    vkResetFences = auto()
    vkWaitForFences = auto()
    vkCreateEvent = auto()
    vkGetEventStatus = auto()
    vkSetEvent = auto()
    vkResetEvent = auto()
    vkCreateQueryPool = auto()
    vkAllocateDescriptorSets = auto()
    vkUpdateDescriptorSets = auto()
    vkBeginCommandBuffer = auto()
    vkEndCommandBuffer = auto()
    vkQueueWaitIdle = auto()
    vkDeviceWaitIdle = auto()
    vkQueueSubmit = auto()
    vkBindBufferMemory = auto()
    vkBindImageMemory = auto()
    vkQueueBindSparse = auto()
    vkCmdBeginRenderPass = auto()
    vkCmdNextSubpass = auto()
    vkCmdExecuteCommands = auto()
    vkCmdEndRenderPass = auto()
    vkCmdBindPipeline = auto()
    vkCmdSetViewport = auto()
    vkCmdSetScissor = auto()
    vkCmdSetLineWidth = auto()
    vkCmdSetDepthBias = auto()
    vkCmdSetBlendConstants = auto()
    vkCmdSetDepthBounds = auto()
    vkCmdSetStencilCompareMask = auto()
    vkCmdSetStencilWriteMask = auto()
    vkCmdSetStencilReference = auto()
    vkCmdBindDescriptorSets = auto()
    vkCmdBindVertexBuffers = auto()
    vkCmdBindIndexBuffer = auto()
    vkCmdCopyBufferToImage = auto()
    vkCmdCopyImageToBuffer = auto()
    vkCmdCopyBuffer = auto()
    vkCmdCopyImage = auto()
    vkCmdBlitImage = auto()
    vkCmdResolveImage = auto()
    vkCmdUpdateBuffer = auto()
    vkCmdFillBuffer = auto()
    vkCmdPushConstants = auto()
    vkCmdClearColorImage = auto()
    vkCmdClearDepthStencilImage = auto()
    vkCmdClearAttachments = auto()
    vkCmdPipelineBarrier = auto()
    vkCmdWriteTimestamp = auto()
    vkCmdCopyQueryPoolResults = auto()
    vkCmdBeginQuery = auto()
    vkCmdEndQuery = auto()
    vkCmdResetQueryPool = auto()
    vkCmdSetEvent = auto()
    vkCmdResetEvent = auto()
    vkCmdWaitEvents = auto()
    vkCmdDraw = auto()
    vkCmdDrawIndirect = auto()
    vkCmdDrawIndexed = auto()
    vkCmdDrawIndexedIndirect = auto()
    vkCmdDispatch = auto()
    vkCmdDispatchIndirect = auto()
    vkCmdDebugMarkerBeginEXT = auto()
    vkCmdDebugMarkerInsertEXT = auto()
    vkCmdDebugMarkerEndEXT = auto()
    vkDebugMarkerSetObjectNameEXT = auto()
    vkCreateSwapchainKHR = auto()
    SetShaderDebugPath = auto()
    vkRegisterDeviceEventEXT = auto()
    vkRegisterDisplayEventEXT = auto()
    vkCmdIndirectSubCommand = auto()
    vkCmdPushDescriptorSetKHR = auto()
    vkCmdPushDescriptorSetWithTemplateKHR = auto()
    vkCreateDescriptorUpdateTemplate = auto()
    vkUpdateDescriptorSetWithTemplate = auto()
    vkBindBufferMemory2 = auto()
    vkBindImageMemory2 = auto()
    vkCmdWriteBufferMarkerAMD = auto()
    vkSetDebugUtilsObjectNameEXT = auto()
    vkQueueBeginDebugUtilsLabelEXT = auto()
    vkQueueEndDebugUtilsLabelEXT = auto()
    vkQueueInsertDebugUtilsLabelEXT = auto()
    vkCmdBeginDebugUtilsLabelEXT = auto()
    vkCmdEndDebugUtilsLabelEXT = auto()
    vkCmdInsertDebugUtilsLabelEXT = auto()
    vkCreateSamplerYcbcrConversion = auto()
    vkCmdSetDeviceMask = auto()
    vkCmdDispatchBase = auto()
    vkGetDeviceQueue2 = auto()
    vkCmdDrawIndirectCount = auto()
    vkCmdDrawIndexedIndirectCount = auto()
    vkCreateRenderPass2 = auto()
    vkCmdBeginRenderPass2 = auto()
    vkCmdNextSubpass2 = auto()
    vkCmdEndRenderPass2 = auto()
    vkCmdBindTransformFeedbackBuffersEXT = auto()
    vkCmdBeginTransformFeedbackEXT = auto()
    vkCmdEndTransformFeedbackEXT = auto()
    vkCmdBeginQueryIndexedEXT = auto()
    vkCmdEndQueryIndexedEXT = auto()
    vkCmdDrawIndirectByteCountEXT = auto()
    vkCmdBeginConditionalRenderingEXT = auto()
    vkCmdEndConditionalRenderingEXT = auto()
    vkCmdSetSampleLocationsEXT = auto()
    vkCmdSetDiscardRectangleEXT = auto()
    DeviceMemoryRefs = auto()
    vkResetQueryPool = auto()
    ImageRefs = auto()
    vkCmdSetLineStippleEXT = auto()
    vkGetSemaphoreCounterValue = auto()
    vkWaitSemaphores = auto()
    vkSignalSemaphore = auto()
    vkQueuePresentKHR = auto()
    vkCmdSetCullModeEXT = auto()
    vkCmdSetFrontFaceEXT = auto()
    vkCmdSetPrimitiveTopologyEXT = auto()
    vkCmdSetViewportWithCountEXT = auto()
    vkCmdSetScissorWithCountEXT = auto()
    vkCmdBindVertexBuffers2EXT = auto()
    vkCmdSetDepthTestEnableEXT = auto()
    vkCmdSetDepthWriteEnableEXT = auto()
    vkCmdSetDepthCompareOpEXT = auto()
    vkCmdSetDepthBoundsTestEnableEXT = auto()
    vkCmdSetStencilTestEnableEXT = auto()
    vkCmdSetStencilOpEXT = auto()
    CoherentMapWrite = auto()
    Max = auto()

pp = pprint.PrettyPrinter(indent=4)

g_is_binding_fbo = True # using this variable to separate passes
g_next_draw_will_add_state = False # using this variable to separate passes
g_markers = []
g_draw_durations = {}

# raw data
g_events = []

markdeep_head = """
<meta charset="utf-8" emacsmode="-*- markdown -*-">
<link rel="stylesheet" href="../src/company-api.css">
<script src="../src/rdc.js" charset="utf-8"></script>
<script src="../src/markdeep.min.js" charset="utf-8"></script>
<script src="../src/lazysizes.js" charset="utf-8"></script>\n
"""

markdeep_lite_head = """
<meta charset="utf-8" emacsmode="-*- markdown -*-">
<link rel="stylesheet" href="../src/company-api.css">
<script src="../src/markdeep.min.js" charset="utf-8"></script>
"""

mermaid_head = """
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>\n
"""

rdc_file = '.rdc'

class TextureDoctor:
    def __init__(self, controller, resource_id):
        self.name = get_resource_name(controller, resource_id, False)
        self.info = get_texture_info(controller, resource_id)
        self.channels = self.info.format.compCount
        self.format = rd.ResourceFormat(self.info.format).Name()

        self.tips = []
 
        # doctor jobs...
        if self.info.creationFlags & rd.TextureCategory.ColorTarget:
            if 'R16G16B16A16_FLOAT' in self.format:
                self.tips.append('64bits_per_pixel')
        name_lower = self.name.lower()
        if 'hud' in name_lower or 'sactx' in name_lower or 'font' in name_lower or 't_fx' in name_lower or 'tex_eft' in name_lower:
            # white-list, "2D" textures, used as HUD, UI etc.
            pass
        elif self.info.creationFlags == rd.TextureCategory.ShaderRead:
            # read-only texture
            pixels = controller.GetTextureData(resource_id, rd.Subresource(0, 0, 0))

            is_single_color = True
            fmt = self.info.format
            stride = fmt.compByteWidth * fmt.compCount
            if fmt.compByteWidth == 1 and fmt.compType == rd.CompType.UNorm:
                unpack_string = 'B' * fmt.compCount
            # elif fmt.compByteWidth == 0 and fmt.compType == rd.CompType.UNorm:
            #     stride = 1 * fmt.compCount
            #     unpack_string = 'B' * fmt.compCount
            elif fmt.compByteWidth == 2 and fmt.compType == rd.CompType.Float:
                unpack_string = 'e' * fmt.compCount
            elif fmt.compByteWidth == 4 and fmt.compType == rd.CompType.Float:
                unpack_string = 'f' * fmt.compCount                
            else:
                unpack_string = ''

            if unpack_string:
                prev_pixel = struct.unpack_from(unpack_string, pixels, 0)
                for i in range(self.info.width * self.info.height):
                    pixel = struct.unpack_from(unpack_string, pixels, i * stride)
                    if prev_pixel != pixel:
                        is_single_color = False
                        break
                    prev_pixel = pixel
        
                if is_single_color:
                    self.tips.append('single_color' + str(prev_pixel))

            if 'lightmap' not in name_lower and (self.info.width > 512 or self.info.height > 512):
                self.tips.append('large_dimension')
            if self.info.width >= 256 and self.info.height >= 256:
                if self.info.mips == 1:
                    self.tips.append('no_mipmap')
                if 'BC' not in self.format and\
                    'ETC' not in self.format and\
                    'EAC' not in self.format and\
                    'ASTC' not in self.format and\
                    'PVRTC' not in self.format:
                    self.tips.append('uncompressed_format')
                if not math.log(self.info.width, 2).is_integer() or\
                    not math.log(self.info.height, 2).is_integer():
                    self.tips.append('not_power_of_two')

            # if tex_info.creationFlags != rd.TextureCategory.ShaderRead:
            # continue

class ShaderDoctor:
    def __init__(self, controller, resource_id):
        pass

'''
PPD (Pass - State - Draw) hierachy, there could be other hierachies, so I need to separate <derived data> from <raw data>

Frame
    - Pass
        - State
            - Draw
                - Event
                - Event
                - Event
            - Draw
            - Draw
        - State
        - State
    - Pass
    - Pass
'''

class Pass:
    # draws on same FBO
    def __init__(self):
        self.pass_id = Pass.s_id
        Pass.s_id += 1
        self.states = []

    def addState(self, draw):
        # if len(self.states) > 0 and self.states[0].getName().find('s_') == 0:
        #     # dummy, replace it
        #     self.states[0] = State(draw)
        #     return

        # print("addState %d" % (len(self.states)))

        new_state = State(draw)
        self.states.append(new_state)
        State.current = self.states[-1]

    def getFirstDraw(self):
        # TODO: this is a wrong assumption, fix it when I have time
        if len(self.states) == 0:
            return None
        return self.states[0].getFirstDraw()

    def getLastDraw(self):
        # TODO: this is a wrong assumption, fix it when I have time
        if len(self.states) == 0:
            return None
        return self.states[-1].getLastDraw()

    def getName(self, controller):
        if self.name:
            return self.name

        pass_info = ""
        if self.getLastDraw():
            # TODO: assume every draws share the same set of targets
            pass_info = self.getLastDraw().getPassSummary(controller)

        if not pass_info:
            self.name = "Pass%d" % (self.pass_id)
        else:
            self.name = "Pass%d__%s" % (self.pass_id, pass_info)

        return self.name

    def writeIndexHtml(self, markdown, controller):
        markdown.write('# %s\n' % (self.getName(controller)))
        for s in self.states:
            s.writeIndexHtml(markdown, controller)

    def exportResources(self, controller):
        for s in self.states:
            s.exportResources(controller)

    def writeDetailHtml(self, controller):
        for s in self.states:
            filename = g_assets_folder / (s.getUniqueName() + '.html')
            if not Path(filename).exists():
                with open(filename,"w") as self_html:
                    s.writeDetailHtml(self_html, controller)
                    print(filename)

    states = None
    pass_id = None
    current = None
    name = None
    s_id = 1

uniqueStateCounters = {}

class State:
    def __init__(self, draw):
        self.events = []
        self.draws = []
        self.name = 'default'
        self.unique_name = self.name
        # TODO: refactor
        self.vs_name = ''
        self.ps_name = ''
        self.cs_name = ''
        State.s_id += 1

        if draw:
            self.name = draw.pso_key
            self.vs_name = draw.short_shader_names[rd.ShaderStage.Vertex]
            self.ps_name = draw.short_shader_names[rd.ShaderStage.Pixel]
            self.cs_name = draw.short_shader_names[rd.ShaderStage.Compute]

            if self.name in uniqueStateCounters:
                uniqueStateCounters[self.name] += 1
                self.unique_name = '%s_%d' % (self.name, uniqueStateCounters[self.name])
            else:
                uniqueStateCounters[self.name] = 0
                self.unique_name = self.name

    def getFirstDraw(self):
        if len(self.draws) == 0:
            return None
        
        return self.draws[0]

    def getLastDraw(self):
        if len(self.draws) == 0:
            return None
        
        return self.draws[-1]

    def getUniqueName(self):
        # used in markdown annotation
        return self.unique_name

    def getName(self):
        return self.name

    def writeIndexHtml(self, markdown, controller):
        markdown.write('## %s\n' % linkable_get_resource_filename(self.getUniqueName(), 'html'))
        # for ev in self.events:
        #     ev.writeIndexHtml(markdown, controller)
        draw_count = len(self.draws)
        if draw_count == 0:
            return

        if draw_count == 1:
            self.draws[0].writeIndexHtml(markdown, controller)
        elif draw_count == 2:
            self.draws[0].writeIndexHtml(markdown, controller)
            self.draws[1].writeIndexHtml(markdown, controller)
        else:
            self.draws[0].writeIndexHtml(markdown, controller)
            self.draws[int(draw_count/2)].writeIndexHtml(markdown, controller)
            self.draws[-1].writeIndexHtml(markdown, controller)

        markdown.write('\n')

    def writeDetailHtml(self, markdown, controller):
        markdown.write(markdeep_head)
        markdown.write('## %s\n' % (self.getUniqueName()))
        for d in self.draws:
            d.writeDetailHtml(markdown, controller)

    def exportResources(self, controller):
        if WRITE_DETALS:
            for d in self.draws:
                d.exportResources(controller)
        else:
            draw_count = len(self.draws)
            if draw_count == 0:
                return
            if draw_count == 1:
                self.draws[0].exportResources(controller)
            elif draw_count == 2:
                self.draws[0].exportResources(controller)
                self.draws[1].exportResources(controller)
            else:
                self.draws[0].exportResources(controller)
                self.draws[int(draw_count/2)].exportResources(controller)
                self.draws[-1].exportResources(controller)

    def addEvent(self, ev):
        self.events.append(ev)

    def addDraw(self, draw):
        self.events.append(draw)
        self.draws.append(draw)

    current = None
    events = None
    draws = None
    s_id = 0

State.default = State(None)

class Event:
    def __init__(self, controller, ev, level = 0):
        global g_is_binding_fbo
        global api_full_log
        global api_short_log
        global g_next_draw_will_add_state

        sdfile = controller.GetStructuredFile()
        chunks = sdfile.chunks
        self.chunk_id = ev.chunkIndex
        self.event_id = ev.eventId
        self.level = level
        # m_StructuredFile->chunks[ev.chunkIndex]->metadata.chunkID
        # C:\svn_pool\renderdoc\renderdoc\driver\gl\gl_driver.cpp

        # struct SDChunkMetaData
        # enum class GLChunk
        cid = chunks[ev.chunkIndex].metadata.chunkID
        if API_TYPE == rd.GraphicsAPI.OpenGL:
            event_type = GLChunk(cid)
        elif API_TYPE == rd.GraphicsAPI.Vulkan:
            event_type = VulkanChunk(cid)
        else:
            event_type = D3D11Chunk(cid)
        self.name = event_type.name

        if self.name.find('Draw') != -1 \
            or self.name.find('Dispatch') != -1:
            g_is_binding_fbo = False
        else:
            api_full_log.write('%s%04d %s\n' % ('    ' * level, self.event_id, self.name))
            if event_type == GLChunk.glBindFramebuffer or \
                event_type == VulkanChunk.vkCmdBeginRenderPass or \
                event_type == D3D11Chunk.OMSetRenderTargets or \
                event_type == D3D11Chunk.OMSetRenderTargetsAndUnorderedAccessViews:
                if not g_is_binding_fbo:
                    # non fbo call -> fbo call, marks start of a new pass
                    api_short_log.write('%se%04d %s\n' % ('    ' * level, self.event_id, self.name))
                    g_next_draw_will_add_state = True
                g_is_binding_fbo = True

    def writeIndexHtml(self, markdown, controller):
        pass

    def exportResources(self, controller):
        pass

    name = None
    event_id = None
    level = None
    event_type = None
    chunk_id = None

class Draw(Event):
    def __init__(self, controller, draw, level = 0):
        global api_full_log
        global api_short_log
        print('draw %d: %s\n' % (draw.drawcallId, draw.name))
        api_full_log.write('%sdraw_%04d %s\n' % ('    ' * level, draw.drawcallId, draw.name))
        api_short_log.write('%s%04d %s\n' % ('    ' * level, draw.drawcallId, draw.name))
        self.draw_desc = draw
        self.event_id = draw.eventId
        self.draw_id = draw.drawcallId
        self.name = draw.name
        self.level = level
        self.pso_key = ''
        self.short_shader_names = [None] * rd.ShaderStage.Count
        self.shader_names = [None] * rd.ShaderStage.Count
        self.shader_cb_contents = [None] * rd.ShaderStage.Count
        self.textures = []
        self.color_buffers = []
        self.depth_buffer = None
        self.expanded_marker = get_expanded_marker_name()
        self.marker = get_marker_name()
        self.gpu_duration = 0
        self.alpha_enabled = False
        if self.event_id in g_draw_durations:
            self.gpu_duration = g_draw_durations[self.event_id]
            if math.isnan(self.gpu_duration) or self.gpu_duration < 0:
                self.gpu_duration = 0

        for output in draw.outputs:
            self.color_buffers.append(output)
        self.depth_buffer = draw.depthOut

        # api_full_log.flush()
        # api_short_log.flush()

    def sharesState(self, other):
        if self.depth_buffer != other.depth_buffer:
            return False
        if len(self.color_buffers) != len(other.color_buffers):
            return False
        for i in range(0, len(self.color_buffers)):
            if self.color_buffers[i] != other.color_buffers[i]:
                return False

        return True

    def isClear(self):
        return 'Clear' in self.name\
            or 'Invalidate' in self.name \
            or 'Discard' in self.name

    def isCopy(self):
        return 'Copy' in self.name

    def isDispatch(self):
        return self.name.find('Dispatch') != -1

    def collectPipeline(self, controller):
        if not WRITE_PIPELINE:
            return

        if self.isClear():
            self.pso_key = 'Clear'

            if self.pso_key != State.current.getName():
                # detects a PSO change
                # TODO: this is too ugly
                # TODO: this is double double ugly
                Pass.current.addState(self)
            return

        if self.isCopy():
            self.pso_key = 'Copy'

            if self.pso_key != State.current.getName():
                Pass.current.addState(self)
            return

        global api_full_log

        if API_TYPE == rd.GraphicsAPI.Vulkan and self.isDispatch():
            # on Android devices, Vulkan dispatch calls will likely crash renderdoc, so we skip them
            self.pso_key = 'compute_shader'
            if self.pso_key != State.current.getName():
                Pass.current.addState(self)
            return

        controller.SetFrameEvent(self.event_id, False)
        # pso
        pso = None
        pipe_state = controller.GetPipelineState()
        pipe = pipe_state.GetGraphicsPipelineObject()

        if API_TYPE == rd.GraphicsAPI.OpenGL:
            pso = controller.GetGLPipelineState()
            # C:\svn_pool\renderdoc\renderdoc\api\replay\gl_pipestate.h
        elif API_TYPE == rd.GraphicsAPI.D3D11:
            pso = controller.GetD3D11PipelineState()
        elif API_TYPE == rd.GraphicsAPI.D3D12:
            pso = controller.GetD3D12PipelineState()
        elif API_TYPE == rd.GraphicsAPI.Vulkan:
            pso = controller.GetVulkanPipelineState()

        program_name = ""

        shader_flags = [
            '--vertex',
            '--tessellation_control',
            '--tessellation_evaluation',
            '--geometry',
            '--fragment',
            '--compute',
        ]
        for stage in range(0, rd.ShaderStage.Count):
            # C:\svn_pool\renderdoc\renderdoc\api\replay\shader_types.h
            # struct ShaderReflection
            # TODO: refactor
            shader = None
            shader_name = None
            short_shader_name = None
            refl = None
            shader_id = pipe_state.GetShader(stage)

            if self.isDispatch():
                if stage != 5:
                    continue
                shader = pso.computeShader
            else:
                if stage == 0:
                    shader = pso.vertexShader
                elif stage == 1:
                    if API_TYPE == rd.GraphicsAPI.OpenGL or API_TYPE == rd.GraphicsAPI.Vulkan:
                        shader = pso.tessControlShader
                    else:
                        shader = pso.hullShader
                elif stage == 2:
                    if API_TYPE == rd.GraphicsAPI.OpenGL or API_TYPE == rd.GraphicsAPI.Vulkan:
                        shader = pso.tessEvalShader
                    else:
                        shader = pso.domainShader
                elif stage == 3:
                    shader = pso.geometryShader
                elif stage == 4:
                    if API_TYPE == rd.GraphicsAPI.OpenGL or API_TYPE == rd.GraphicsAPI.Vulkan:
                        shader = pso.fragmentShader
                    else:
                        shader = pso.pixelShader
                elif stage == 5:
                    continue

            if shader_id != rd.ResourceId.Null():
                # api_full_log.write(str(shader_id))
                # api_full_log.write('\n')
                refl = pipe_state.GetShaderReflection(stage)
                if hasattr(shader, 'programResourceId'):
                    # Opengl
                    program_name = get_resource_name(controller, shader.programResourceId)
                    short_shader_name = get_resource_name(controller, shader.shaderResourceId)
                    shader_name = program_name + '__' + short_shader_name
                elif hasattr(pso, 'pipelineResourceId'):
                    # DX12
                    program_name = get_resource_name(controller, pso.pipelineResourceId)
                    program_name = program_name.replace('Pipeline_State', 'pso')
                    short_shader_name = get_resource_name(controller, shader_id)
                    shader_name = program_name + '__' + short_shader_name
                elif hasattr(pso, 'graphics') or hasattr(pso, 'compute'):
                    # Vulkan
                    p = pso.graphics or pso.graphics
                    program_name = get_resource_name(controller, p.pipelineResourceId)
                    program_name = program_name.replace('Pipeline', 'pso')
                    short_shader_name = get_resource_name(controller, shader_id)
                    # .replace('Shader_Module', 'shader')
                    if 'Shader_Module' in short_shader_name:
                        shader_name = program_name + '__' + ShaderStage(stage).name
                    else:
                        program_name = short_shader_name 
                        shader_name = short_shader_name + '__' + ShaderStage(stage).name
                else:
                    short_shader_name = get_resource_name(controller, shader_id)
                    short_shader_name = short_shader_name.replace('Vertex_Shader', 'vs').replace('Pixel_Shader', 'ps').replace('Compute_Shader', 'cs').replace('Shader_Module', 'shader').replace('Geometry_Shader', 'gs')
                    if program_name and short_shader_name not in program_name:
                            # Skip duplicated shader names in same program
                            program_name += '__'
                            program_name += short_shader_name
                    else:
                        program_name = 's_' + short_shader_name
                    shader_name = short_shader_name
                self.shader_names[stage] = shader_name
                self.short_shader_names[stage] = short_shader_name

            if refl:
                if WRITE_CONST_BUFFER:
                    self.shader_cb_contents[stage] = get_cbuffer_contents(controller, stage, self.shader_names[stage], refl, program_name)

                    # const_buffer--%4d.html
                    resource_name = 'const_buffer--%04d' % (self.draw_id)
                    file_name = get_resource_filename(g_assets_folder / resource_name, 'html')
                    if not Path(file_name).exists():
                        with open(file_name, 'w') as fp:
                            fp.write(markdeep_head)
                            for s in range(0, rd.ShaderStage.Count):
                                # TODO:
                                if self.shader_cb_contents[s]:
                                    fp.write('# %s\n' % (ShaderStage(s).name)) # shader type head "VS", "FS" etc
                                    fp.write('```glsl\n')
                                    fp.write(self.shader_cb_contents[s])
                                    fp.write('\n```\n')
                                    fp.write("\n\n")
                if False:
                    # TODO: sadly ShaderBindpointMapping is always empty :(
                    mapping = shader.bindpointMapping # struct ShaderBindpointMapping
                    for sampler in mapping.samplers:
                        print(sampler.name)

                if False:
                    samplers = pipe_state.GetSamplers(stage)
                    for sampler in samplers:
                        print(sampler)

                if self.color_buffers and self.color_buffers[0] != rd.ResourceId.Null():
                    blends = pipe_state.GetColorBlends()
                    for blend in blends:
                        if blend.enabled:
                            self.alpha_enabled = True
                # raw txt
                txt_file_name = get_resource_filename(g_assets_folder / shader_name, 'txt')

                if not Path(txt_file_name).exists():
                    with open(txt_file_name, 'wb') as fp:
                        print("Writing %s" % txt_file_name)
                        fp.write(refl.rawBytes)

                # html
                html_file_name = get_resource_filename(g_assets_folder / shader_name, 'html')
                if not Path(html_file_name).exists():
                    highlevel_shader = ''
                    shader_analysis = ''
                    if API_TYPE == rd.GraphicsAPI.OpenGL or API_TYPE == rd.GraphicsAPI.Vulkan:
                        if API_TYPE == rd.GraphicsAPI.OpenGL:
                            highlevel_shader = str(refl.rawBytes, 'utf-8')
                            highlevel_shader = highlevel_shader.replace('<', ' < ') # fix a glsl syntax bug
                            lang = '--opengles'
                        else:
                            targets = controller.GetDisassemblyTargets(True)
                            for t in targets:
                                highlevel_shader = controller.DisassembleShader(pipe, refl, t)
                                break
                            lang = '--vulkan'

                        malioc_exe = g_assets_folder / '../' / 'mali_offline_compiler/malioc.exe'
                        if WRITE_MALIOC and  malioc_exe.exists():
                            args = [
                                str(malioc_exe),
                                shader_flags[stage],
                                lang,
                                txt_file_name
                            ]
                            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
                            shader_analysis, _ = proc.communicate()
                            shader_analysis = str(shader_analysis, 'utf-8')
                            shader_analysis = shader_analysis.replace('\r\n\r\n', '\n')
                    else:
                        targets = controller.GetDisassemblyTargets(True)
                        for t in targets:
                            highlevel_shader = controller.DisassembleShader(pipe, refl, t)
                            break

                    with open(html_file_name, 'w') as fp:
                        print("Writing %s" % html_file_name)
                        fp.write(markdeep_lite_head)
                        fp.write('# marker\n %s\n' % self.expanded_marker)
                        if shader_analysis:
                            fp.write('# analysis\n```\n%s \n```\n' % shader_analysis)
                        fp.write('# shader\n')
                        fp.write('```glsl\n')
                        fp.write(highlevel_shader)
                        fp.write('\n```\n')
                        fp.write("\n\n")

                # C:\svn_pool\renderdoc\renderdoc\api\replay\gl_pipestate.h
                # struct State

                # TODO: deal with other resources, (atomicBuffers, uniformBuffers, shaderStorageBuffers, images, transformFeedback etc)
                if hasattr(pso, 'textures') and not self.textures:
                    for idx, sampler in enumerate(pso.samplers):
                        # TODO: why is sampler always zero?
                        resource_id = sampler.resourceId
                        if resource_id == rd.ResourceId.Null():
                            continue
                        # print(sampler.minLOD)

                    for idx, texture in enumerate(pso.textures):
                        resource_id = texture.resourceId
                        if resource_id == rd.ResourceId.Null():
                            continue
                        g_frame.textures.add(resource_id)
                        self.textures.append(resource_id)
        self.pso_key = program_name

        if self.pso_key != State.current.getName():
            # detects a PSO change
            # TODO: this is too ugly
            Pass.current.addState(self)

    def getPassSummary(self, controller):
        summary = ''
        color_count = 0
        depth_count = 0
        texture_info = None
        for resource_id in self.color_buffers:
            if resource_id != rd.ResourceId.Null():
                color_count += 1
                if not texture_info:
                    texture_info = get_texture_info(controller, resource_id)
        if self.depth_buffer != rd.ResourceId.Null():
            depth_count += 1
            if not texture_info:
                texture_info = get_texture_info(controller, self.depth_buffer)            
        if depth_count > 0:
            summary = 'z'
        else:
            summary = ''
        if color_count > 0:
            if color_count == 1:
                summary += 'c'
            else:
                summary += '%dc' % (color_count)

        if texture_info:
            summary = '%s_%dX%d' % (summary, texture_info.width, texture_info.height)
        return summary

    def writeTextureMarkdown(self, markdown, controller, caption_suffix, resource_id, texture_file_name):
        texture_info = get_texture_info(controller, resource_id)
        depth_info = ''
        arraysize_info = ''
        mips_info = ''
        if texture_info.depth > 1:
            depth_info = 'x%d' % texture_info.depth
        if texture_info.arraysize > 1:
            arraysize_info = '[%d]' % texture_info.arraysize
        if texture_info.mips > 1:
            mips_info = '%d mips ' % texture_info.mips
        texture_info_text = '(%dX%d%s%s %s%s)' % (texture_info.width, texture_info.height, depth_info, arraysize_info, mips_info, rd.ResourceFormat(texture_info.format).Name() )

        # enum class ResourceFormatType
        # rdcstr ResourceFormatName(const ResourceFormat &fmt)
        # markdown.write('<img src="%s" class="lazyload" data-src="%s" width=%s border="2">\n' % ('../src/logo.png', texture_file_name, '50%'))
        # caption_suffix, texture_info_text
        markdown.write('![%s `%s`](%s class="lazyload" data-src="%s" border="2")' % (caption_suffix, texture_info_text, "../src/logo.png", texture_file_name))
        # markdown.write('![%s `%s`](%s class="lazyload" loading="lazy" border="2")' % (caption_suffix, texture_info_text, texture_file_name))
    
    def writeDetailHtml(self, markdown, controller):
        self.writeIndexHtml(markdown, controller)
        sdfile = controller.GetStructuredFile()
        chunks = sdfile.chunks

        for ev in self.draw_desc.events:
            cid = chunks[ev.chunkIndex].metadata.chunkID
            if API_TYPE == rd.GraphicsAPI.OpenGL:
                event_type = GLChunk(cid)
            elif API_TYPE == rd.GraphicsAPI.Vulkan:
                event_type = VulkanChunk(cid)
            else:
                event_type = D3D11Chunk(cid)
            markdown.write("`event_%04d %s`\n\n" % (ev.eventId, event_type.name))

        markdown.write('\n\n--------\n\n')
        markdown.write('\n\n--------\n\n')

    def writeIndexHtml(self, markdown, controller):
        global g_assets_folder

        markdown.write('### [D]%04d %s\n\n' % (self.draw_id, self.name.replace('#', '__')))

        if self.expanded_marker:
            markdown.write('%s\n\n' % self.expanded_marker)
    
        if self.isClear() or self.isCopy():
            # to improve draw-level navigation by pressing 'd' and 'D'
            markdown.write('<br><br>\n\n')
        else:
            markdown.write('Blends: %s\n\n' % ("Enabled" if self.alpha_enabled else "Disabled"))
        
            # shader section
            for stage in range(0, rd.ShaderStage.Count):
                if self.shader_names[stage] != None:
                    # TODO: refactor
                    markdown.write("%s: %s " % (ShaderStage(stage).name, linkable_get_resource_filename(self.shader_names[stage], 'html')))

            # cb / constant buffer section
            if WRITE_CONST_BUFFER:
                resource_name = 'const_buffer--%04d' % (self.draw_id)
                file_name = get_resource_filename(resource_name, 'html')
                markdown.write("CB: %s" % (link_to_file(resource_name, file_name)))

            markdown.write('\n\n')

        if not self.isDispatch():
            # color buffer section
            if WRITE_COLOR_BUFFER:
                for idx, resource_id in enumerate(self.color_buffers):
                    if not resource_id or resource_id == rd.ResourceId.Null():
                        continue
                    resource_name = get_resource_name(controller, resource_id)
                    # TODO: ugly
                    file_name = get_resource_filename('%s--%04d_c%d' % (resource_name, self.draw_id, idx), IMG_EXT)
                    self.writeTextureMarkdown(markdown, controller, 'c%d: %s' % (idx, resource_name), resource_id, file_name)
            
            # depth buffer section
            if WRITE_DEPTH_BUFFER:
                if self.depth_buffer != rd.ResourceId.Null():
                    resource_id = self.depth_buffer
                    resource_name = get_resource_name(controller, resource_id)
                    # TODO: ugly again
                    file_name = get_resource_filename('%s--%04d_z' % (resource_name, self.draw_id), IMG_EXT)
                    self.writeTextureMarkdown(markdown, controller, 'z: %s' % (resource_name), resource_id, file_name)

            # texture section
            markdown.write('\n\n--------\n\n')
            if not self.isClear() and not self.isCopy() and WRITE_TEXTURE:
                for idx, resource_id in enumerate(self.textures):
                    if not resource_id or resource_id == rd.ResourceId.Null():
                        continue
                    # if idx > 7: # magic
                        # TODO: uglllllly
                        # break
                    resource_name = get_resource_name(controller, resource_id)
                    file_name = get_resource_filename(resource_name, IMG_EXT)
                    self.writeTextureMarkdown(markdown, controller, 't%s: %s' % (idx, resource_name), resource_id, file_name)
        markdown.write('\n\n')
        # TODO: add UAV / image etc

    def exportResources(self, controller):
        if not WRITE_COLOR_BUFFER and not WRITE_DEPTH_BUFFER and not WRITE_TEXTURE:
            return

        if API_TYPE == rd.GraphicsAPI.Vulkan and self.isDispatch():
            # on Android devices, Vulkan dispatch calls will likely crash renderdoc, so we skip them
            return

        if WRITE_COLOR_BUFFER or WRITE_DEPTH_BUFFER:
            controller.SetFrameEvent(self.event_id, False)

        # WRITE textures
        if WRITE_TEXTURE:
            for idx, resource_id in enumerate(self.textures):
                if resource_id == rd.ResourceId.Null():
                    continue
                resource_name = get_resource_name(controller, resource_id)
                file_name = get_resource_filename(resource_name, IMG_EXT)
                export_texture(controller, resource_id, file_name)
                
        # WRITE render targtes (aka outputs)
        if WRITE_COLOR_BUFFER:
            for idx, resource_id in enumerate(self.color_buffers):
                if resource_id != rd.ResourceId.Null():
                    resource_name = get_resource_name(controller, resource_id)
                    file_name = get_resource_filename('%s--%04d_c%d' % (resource_name, self.draw_id, idx), IMG_EXT)
                    if WRITE_COLOR_BUFFER:
                        export_texture(controller, resource_id, file_name)

        # depth
        if WRITE_DEPTH_BUFFER and self.depth_buffer:
            resource_id = self.depth_buffer
            if resource_id != rd.ResourceId.Null():
                resource_name = get_resource_name(controller, resource_id)
                file_name = get_resource_filename('%s--%04d_z' % (resource_name, self.draw_id), IMG_EXT)
                if not Path(file_name).exists():
                    export_texture(controller, resource_id, file_name)

    draw_id = None
    draw_desc = None # struct DrawcallDescription
    shader_names = None
    pso_key = None
    color_buffers = None
    depth_buffer = None

def export_texture(controller, resource_id, file_name):
    global g_assets_folder

    file_path = g_assets_folder / file_name
    if file_path.exists():
        return

    file_name = str(file_path)
    texture_info = get_texture_info(controller, resource_id)

    texsave = rd.TextureSave()
    fmt = rd.ResourceFormat(texture_info.format).Name()
    if texture_info.format.compCount == 3 or 'A2' in fmt or 'A16' in fmt:
        texsave.alpha = rd.AlphaMapping.Discard
    else:
        texsave.alpha = rd.AlphaMapping.BlendToCheckerboard
    texsave.destType = rd.FileType.JPG
    texsave.mip = 0
    texsave.slice.sliceIndex = 0
    texsave.resourceId = resource_id

    print("Writing %s" % file_name)
    controller.SaveTexture(texsave, file_name)

    if not 'pyrenderdoc' in globals() and texture_info.creationFlags & rd.TextureCategory.DepthTarget:
        # equalizeHist
        try:
            import cv2
            import numpy as np
        except ImportError as error:
            return

        z_rgb = cv2.imread(file_name)
        z_r = z_rgb[:, :, 2]
        equ = cv2.equalizeHist(z_r)
        # res = np.hstack((z_r,equ)) #stacking images side-by-side
        cv2.imwrite(file_name, equ)

def pretty_number(num):
    if num < 1e3:
        return str(num)
    if num < 1e6:
        return "%.1fK" % (num/1e3)
    if num < 1e9:
        return "%.1fM" % (num/1e6)
    return str(num)

class Frame:
    # 
    def __init__(self):
        self.passes = []
        self.textures = set()
        self.shaders = OrderedDict()

        self.addPass()
        self.stateNameDict = defaultdict(int)

    def addPass(self):
        # print("addPass %d" % (len(self.passes)))
        State.current = State.default

        self.passes.append(Pass())
        Pass.current = self.passes[-1]

    def getImageLinkOrNothing(self, filename, width='50%'):
        if not filename:
            return ''

        return '![](%s border="2" width="%s")' % (filename, width)

    def writeShaderOverview(self, markdown, controller):
        markdown.write('# Shader Overview\n')
        markdown.write('name|type|unused_uniforms\n')
        markdown.write('----|----|--------------\n')

        for k,v in g_frame.shaders.items():
            unused_uniforms = ''
            for uk in v['uniforms']:
                uniform = v['uniforms'][uk]
                if not uniform['used']:
                    unused_uniforms += (uk + '<br>')

            markdown.write('[%s](%s.html)|%s|%s\n' % (k, k, v['type'], 
                                            unused_uniforms))

        markdown.write('\n')

    def writeResourceOverview(self, markdown, controller):

        if API_TYPE != rd.GraphicsAPI.OpenGL:
            # TODO: support other formats
            return

        texture_array = []

        for resource_id in g_frame.textures:
            if not resource_id or resource_id == rd.ResourceId.Null():
                continue
            texture_array.append(TextureDoctor(controller, resource_id))

        def getName(elem):
            return elem.name

        def getTipsLength(elem):
            return len(elem.tips)

        texture_array = sorted(texture_array, key=getName)
        texture_array = sorted(texture_array, key=getTipsLength, reverse=True)

        markdown.write('# Resource Overview\n')

        markdown.write('name|type|usage|dimension|mips|format|channels|bytes|tips|preview\n')
        markdown.write('----|----|-----|--------:|---:|------|--------|-----|----|-------\n')
        
        for tex_pair in texture_array:
            file_name = get_resource_filename(getSafeName(tex_pair.name), IMG_EXT)
            tex_info = tex_pair.info
            export_texture(controller, tex_info.resourceId, file_name)
            texType = '%s' % rd.TextureType(tex_info.type)
            category = '%s' % rd.TextureCategory(tex_info.creationFlags)
            markdown.write('%s|%s|%s|%s|%d|%s|%d|%s|%s|%s\n' % (
                tex_pair.name,
                texType.replace('TextureType.Texture', ''),
                category.replace('TextureCategory.', '').replace('ShaderRead','T').replace('ColorTarget','C').replace('DepthTarget','Z').replace('|',''),
                '%dx%d' % (tex_info.width, tex_info.height),
                tex_info.mips,
                tex_pair.format,
                tex_pair.channels,
                pretty_number(tex_info.byteSize),
                '<br>'.join(tex_pair.tips),
                '![](%s class="lazyload" data-src="%s" width="%s")' % ('../src/logo.png', file_name, '20%')
            ))

        markdown.write('\n')

    def writeFrameOverview(self, markdown, controller):
        summary_csv = open(g_assets_folder / 'summary.csv',"w") 

        markdown.write('# Frame Overview\n')

        header = 'pass|state|(ms)|marker|draws|instances|verts|z|c\n'
        summary_csv.write(header.replace('|',','))
        markdown.write(header)
        markdown.write('----|-----|---:|------|----:|--------:|----:|-|-\n')
        overviewText = ''

        # TODO: so ugly
        totalPasses = 0
        totalTime = 0
        totalStates = 0
        totalDraws = 0
        totalInstances = 0
        totalCalls = 0
        totalVerts = 0
        has_clear_state = False
        has_copy_state = False
        for p in self.passes:

            lastDraw = p.getLastDraw()
            if not lastDraw:
                continue

            statesSummary = ''
            timeSummary = ''
            markersSummary = ''
            drawsSummary = ''
            callsSummary = ''
            vertsSummary = ''
            instancesSummary = ''

            time = 0
            draws = 0
            instances = 0
            states = 0
            calls = 0
            verts = 0
            for s in p.states:
                statesSummary += '[%s](#%s/%s)<br>' % (s.getName(), p.getName(controller).lower(), s.getUniqueName().lower())
                drawsSummary += '[%d](%s.html)<br>' % (len(s.draws), s.getUniqueName())

                c = 0
                v = 0
                i = 0
                m = 0
                draws += len(s.draws)
                for d in s.draws:
                    if d.isClear() or d.isCopy():
                        continue
                    c += len(d.draw_desc.events)
                    if d.draw_desc.numInstances > 1:
                        i += d.draw_desc.numInstances
                        v += d.draw_desc.numIndices * d.draw_desc.numInstances
                    else:
                        v += d.draw_desc.numIndices
                    m += d.gpu_duration * 1e3

                callsSummary += '%d<br>' % c
                vertsSummary += '%s<br>' % pretty_number(v)
                instancesSummary += '%d<br>' % i
                if m > 0.5:
                    markersSummary += '<b>%s</b><br>' % s.draws[-1].marker
                    timeSummary += '<b>%.2f</b><br>' % m
                else:
                    markersSummary += '%s<br>' % s.draws[-1].marker
                    timeSummary += '%.2f<br>' % m

                summary_csv.write('%s,%s,%.3f,%s,%d,%d,%d,%s,%s\n' %(p.getName(controller).lower(), s.getName(), m, s.draws[-1].marker, 
                    len(s.draws), i, v, 
                    s.vs_name or s.cs_name, s.ps_name or ''))

                time += m
                calls += c
                verts += v
                if s.getName() is 'Clear':
                    # Clear is not a "correct" State..
                    has_clear_state = True
                elif s.getName() is 'Copy':
                    # Copy is not a "correct" State..
                    has_copy_state = True
                else:
                    states += 1
                instances += i

            if states > 1:
                statesSummary += '~%d<br>' % states
                drawsSummary += '~%d<br>' % draws
                instancesSummary += '~%d<br>' % instances
                callsSummary += '~%d<br>' % calls
                vertsSummary += '~%s<br>' % pretty_number(verts)
                markersSummary += '<br>'
                timeSummary += '~%.2f<br>' % time

            # total stats
            totalPasses += 1
            totalTime += time
            totalStates += states
            totalInstances += instances
            totalDraws += draws
            totalCalls += calls
            totalVerts += verts

            z_filename = ''
            c_info = ''

            if totalVerts != 0:
                c_filenames = [''] * len(lastDraw.color_buffers)
                for idx, resource_id in enumerate(lastDraw.color_buffers):
                    if not resource_id or resource_id == rd.ResourceId.Null():
                        continue
                    resource_name = get_resource_name(controller, resource_id)
                    c_filenames[idx] = get_resource_filename('%s--%04d_c%d' % (resource_name, lastDraw.draw_id, idx), IMG_EXT)
                
                # depth buffer section
                if WRITE_DEPTH_BUFFER:
                    if lastDraw.depth_buffer != rd.ResourceId.Null():
                        resource_id = lastDraw.depth_buffer
                        resource_name = get_resource_name(controller, resource_id)
                        z_filename = get_resource_filename('%s--%04d_z' % (resource_name, lastDraw.draw_id), IMG_EXT)

                for c in c_filenames:
                    if 'bloom' in statesSummary.lower() or 'bloom' in markersSummary.lower():
                        # Save html space for Bloom passes
                        c_info += self.getImageLinkOrNothing(c, '10%')
                    else:
                        c_info += self.getImageLinkOrNothing(c)
                    
            overviewText += ('[%s](#%s)|%s|%s|%s|%s|%s|%s|%s|%s\n' % 
            (p.getName(controller), p.getName(controller).lower(), statesSummary, timeSummary, markersSummary, drawsSummary, instancesSummary, vertsSummary, self.getImageLinkOrNothing(z_filename), c_info))
        
        uniqueStateCounter = len(uniqueStateCounters)
        if has_clear_state:
            # remove "Clear" state
            uniqueStateCounter -= 1
        if has_copy_state:
            # remove "Copy" state
            uniqueStateCounter -= 1            
        overviewText = ('%s|%s|%s|''|[%s](api_short.txt)|%s|%s|%s|%s\n' % 
        ('total: %d' % totalPasses, 'total: %d<br>unique: %d' % (totalStates, uniqueStateCounter), '%.2f' % totalTime, '%d' % totalDraws, '%d' % totalInstances, pretty_number(totalVerts), '', '')) + overviewText
        
        markdown.write(overviewText)
        markdown.write('\n')

    def writeBindStats(self, markdown, label, item):
        # TODO: add redundants
        markdown.write('%s|%d|%d|%d\n' % (label, item.calls, item.sets, item.nulls))

    def getUniqueStateName(self, passName, stateName):
        if self.stateNameDict[stateName] == 1:
            return stateName
        return '%s_%s' % (passName, stateName)

    def writeDAG(self):
        filename = g_assets_folder / 'dag.html' # TODO: ugly
        markdown = open(filename, 'w')
        markdown.write(mermaid_head)
        markdown.write('<div class="mermaid">\n')
        markdown.write('flowchart LR\n')
        pass_count = len(self.passes)

        # subgraph
        for i in range(0, pass_count):
            p = self.passes[i]
            markdown.write('subgraph %s\n' % (p.getName(controller)))

            if True:
                # set sort
                states = list(p.stateNames)
                state_count = len(states)
                if state_count == 1:
                    # no siblings
                    markdown.write('%s\n' % (self.getUniqueStateName(p.getName(controller), states[0])))
                else:
                    for j in range(0, state_count - 1):
                        markdown.write('%s --> %s\n' % (self.getUniqueStateName(p.getName(controller), states[j]), self.getUniqueStateName(p.getName(controller), states[j+1])))
            else:
                state_count = len(p.states)
                if state_count == 1:
                    # no siblings
                    markdown.write('%s\n' % (p.states[0].getUniqueName()))
                else:
                    for j in range(0, state_count - 1):
                        markdown.write('%s --> %s\n' % (p.states[j].getUniqueName(), p.states[j+1].getUniqueName()))

            markdown.write('end\n')

            if i < pass_count - 1:
                # connect neighboring passes, only valid in "flowchart"
                next = self.passes[i+1]
                markdown.write('%s -.-> %s\n' % (p.getName(controller), next.getName()))
        markdown.writelines('</div>\n\n')
        
        # linear order
        dag = set()
        # markdown.write('<h1>PSO diagram</h1>\n')
        # markdown.write('<div class="mermaid">\n')
        # markdown.write('graph LR\n')

        # state_count = len(g_states)
        
        # for i in range(1, state_count):
        #     src = g_states[i]
        #     markdown.write('%s ==> %s\n' % (g_states[i-1].name, g_states[i].name))
        #     for c in src.getFirstDraw().color_buffers:
        #         if c == rd.ResourceId.Null():
        #             continue
        #         for j in range(i+1, state_count):
        #             dst = g_states[j]
        #             for t in dst.getFirstDraw().textures:
        #                 if t == rd.ResourceId.Null():
        #                     continue                        
        #                 if c == t:
        #                     # src.c becomes dst.t
        #                     dag.add((src, dst, get_resource_name(controller, c)))

        # # TODO: merge linear sort and topology sort
        # for src, dst, c in dag:
        #     markdown.write('%s -.->|%s| %s\n' % (src.name, c, dst.name))

        # markdown.writelines('</div>\n\n')

    #   A[Client] -->|tcp_123| B(Load Balancer)
    #   B -->|tcp_456| C[Server1]
    #   B -->|tcp_456| D[Server2]

        markdown.close()

    def writeAPIOverview(self, markdown, controller):
        info = controller.GetFrameInfo()
        stats = info.stats
        if not stats.recorded:
            return

        markdown.write('# API Overview\n')
        markdown.write('## Draw Call Statistics\n')

        markdown.write('type | calls | instanced | indirect\n')
        markdown.write('--------- | ----- | --------- | -------\n')
        markdown.write('%s|%d|%d|%d\n' % ('Draw', stats.draws.calls, stats.draws.instanced, stats.draws.indirect))
        markdown.write('%s|%d|%d|%d\n' % ('Dispatch', stats.dispatches.calls, 0, stats.dispatches.indirect))

        markdown.write('## Resource Update Statistics\n')
        markdown.write('calls | cpu_written | cpu_written\n')
        markdown.write('----- | --------- | -------\n')
        markdown.write('%d|%d|%d\n' % (stats.updates.calls, stats.updates.clients, stats.updates.servers))

        markdown.write('## Resource Bind Statistics\n')
        markdown.write('type | calls | sets | nulls\n')
        markdown.write('---------- | ----- | ---- | -----\n')
        # self.writeBindStats(markdown, stats.updates)
        # markdown.write('%s|%s|%s' % (stats.updates.calls, stats.updates.clients, stats.updates.servers))
        self.writeBindStats(markdown, 'index buffer binds', stats.indices)
        self.writeBindStats(markdown, 'vertex buffer binds', stats.vertices)
        self.writeBindStats(markdown, 'vertex layout binds', stats.layouts)
        # self.writeBindStats(markdown, 'shader bind statistics', stats.shaders)
        self.writeBindStats(markdown, 'blend state binds', stats.blends)
        self.writeBindStats(markdown, 'depth-stencil state binds', stats.depths)
        self.writeBindStats(markdown, 'rasterizer state binds', stats.rasters)
        self.writeBindStats(markdown, 'output merger and UAV binds', stats.outputs)
        markdown.write('\n\n')

    def writeIndexHtml(self, markdown, controller):

        pipelineTypes = [
                "D3D11",
                "D3D12",
                "OpenGL",
                "Vulkan",
        ]
        GPUVendors = [
            "Unknown",
            "ARM",
            "AMD",
            "Broadcom",
            "Imagination",
            "Intel",
            "nVidia",
            "Qualcomm",
            "Verisilicon",
            "Software",
        ]

        api_prop = controller.GetAPIProperties()

        # Header
        markdown.write(markdeep_head)
        markdown.write("**render-doctor %s**\n\n" % (rdc_file))

        self.writeFrameOverview(markdown, controller)
        self.writeShaderOverview(markdown, controller)
        self.writeResourceOverview(markdown, controller)
        self.writeAPIOverview(markdown, controller)

        for p in self.passes:
            p.writeIndexHtml(markdown, controller)

        markdown.write("## Usage\n\n")
        markdown.write("  * Press `p` / `shift+p` to jump between Passes\n")
        markdown.write("  * Press `s` / `shift+s` to jump between States\n")
        markdown.write("  * Press `d` / `shift+d` to jump between Draws\n")
        
        markdown.write('\n--------\n')
        
        markdown.write("## Summary\n\n")
        if WRITE_PSO_DAG:
            markdown.write("  * Experimental feature [pipeline dag](dag.html)\n")
        markdown.write("  * RDC: %s\n" % rdc_file)
        markdown.write("  * API: %s\n" % pipelineTypes[api_prop.pipelineType])
        # markdown.write("  * Replay API: %s\n" % pipelineTypes[api_prop.localRenderer])
        markdown.write("  * GPU: %s\n" % GPUVendors[api_prop.vendor])

        markdown.close()

        if WRITE_PSO_DAG:
            self.writeDAG()

    def exportResources(self, controller):
        print('^exportResources')
        for p in self.passes:
            p.exportResources(controller)
        print('$exportResources')

g_frame = Frame()

class Resource:
    pass

g_assets_folder = None

def get_resource_filename(name, ext = 'txt'):
    return '%s.%s' % (name, ext)

def link_to_file(resource_name, file_name):
    return '[%s](%s)' % (resource_name, file_name)

def linkable_get_resource_filename(name, ext = 'txt'):
    return link_to_file(name, get_resource_filename(name, ext))

def linkable_ResID(id):
    return "[ResID_%s](#ResID_%s)" % (id, id)

def anchor_ResID(id):
    return "<a name=ResID_%s></a>ResID_%s" % (id, id)

def setup_rdc(filename, adb_mode = None):

    if adb_mode:
        # protocols = rd.GetSupportedDeviceProtocols()
        protocol_to_use = 'adb'
        protocol = rd.GetDeviceProtocolController(protocol_to_use)
        devices = protocol.GetDevices()

        if len(devices) == 0:
            raise RuntimeError(f"no {protocol_to_use} devices connected")

        # Choose the first device
        dev = devices[0]
        name = protocol.GetFriendlyName(dev)

        print(f"Running test on {dev} - named {name}")

        URL = protocol.GetProtocolName() + "://" + dev

    rd.InitialiseReplay(rd.GlobalEnvironment(), [])

    cap = rd.OpenCaptureFile()

    # Open a particular file - see also OpenBuffer to load from memory
    status = cap.OpenFile(rdc_file, '', None)
    print("cap.OpenFile")

    # Make sure the file opened successfully
    if status != rd.ReplayStatus.Succeeded:
        raise RuntimeError("Couldn't open file: " + str(status))

    # Make sure we can replay
    if not cap.LocalReplaySupport():
        raise RuntimeError("Capture cannot be replayed")

    # Initialise the replay
    status,controller = cap.OpenCapture(rd.ReplayOptions(), None)
    print("cap.OpenCapture")

    if status != rd.ReplayStatus.Succeeded:
        raise RuntimeError("Couldn't initialise replay: " + rd.ReplayStatus(status).name)

    return cap, controller

def get_expanded_marker_name():
    sep = ' / '
    return sep.join(g_markers)

def get_marker_name():
    if len(g_markers) > 0:
        name = g_markers[-1]
        if 'Colour_Pass' in name:
            return ''
        if len(g_markers) > 1 and name in ['Shadows.Draw', 'ShadowLoopNewBatcher.Draw', 'RenderLoop.Draw', 'RenderLoopNewBatcher.Draw']:
            # to make Unity reports prettier
            name = g_markers[-2]
        max_name_length = 40
        if len(name) > max_name_length:
            name = name[0 : max_name_length-3] + '...'
        return name
    return ''

# Define a recursive function for iterating over draws
def visit_draw(controller, draw, level = 0):
    # hack level
    global g_markers, g_next_draw_will_add_state
    global api_full_log, api_short_log
    if draw.name == 'API Calls':
        pass
    
    needsPopMarker = False
    # print(rd.GLChunk.glPopGroupMarkerEXT)
    if draw.events:
        # api before this draw & including this draw
        for ev in draw.events:
            new_event = Event(controller, ev, level)
            State.current.addEvent(new_event)

        if  draw.flags & rd.DrawFlags.Drawcall \
            or draw.flags & rd.DrawFlags.Dispatch \
            or draw.flags & rd.DrawFlags.MultiDraw \
            or draw.flags & rd.DrawFlags.Clear \
            or draw.flags & rd.DrawFlags.Copy:
            new_draw = Draw(controller, draw, level)

            if g_next_draw_will_add_state:
                # and check duplicated binds...
                g_next_draw_will_add_state = False
                prev_draw = State.current.getLastDraw()
                if not prev_draw:
                    g_frame.addPass()
                elif not new_draw.sharesState(prev_draw):
                    g_frame.addPass()

            new_draw.collectPipeline(controller)
            State.current.addDraw(new_draw)
    else:
        # regime call, skip for now
        # TODO: leverate getSafeName()
        api_full_log.write('%s%04d %s\n' % ('    ' * level, draw.eventId, draw.name))
        api_short_log.write('%s%04d %s\n' % ('    ' * level, draw.drawcallId, draw.name))
        items = draw.name.replace('|',' ').replace('(',' ').replace(')',' ').replace('-',' ').replace('=>',' ').replace('#',' ').split()
        name = '_'.join(items)

        g_markers.append(name)
        needsPopMarker = True

    # Iterate over the draw's children
    for draw in draw.children:
        visit_draw(controller, draw, level + 1)

    if needsPopMarker:
        g_markers.pop()

    return True

def get_texture_info(controller, resource_id):
    # struct TextureDescription
    if resource_id == rd.ResourceId.Null():
        return None

    textures = controller.GetTextures()
    for res in textures:
        if resource_id == res.resourceId:
            return res
    
    return None

resource_name_count = {}
resource_name_dict = {}

def get_resource_name(controller, resource_id, get_safe_name = True):
    if resource_id == rd.ResourceId.Null():
        return "NULL"

    if resource_id not in resource_name_dict:
        resource_name_dict[resource_id] = 'res_%d' % int(resource_id)

        resources = controller.GetResources()
        for res in resources:
            if resource_id == res.resourceId:
                name = res.name
                count = 0
                if name in resource_name_count:
                    resource_name_count[name] += 1
                    count = resource_name_count[name]
                else:
                    resource_name_count[name] = count

                if get_safe_name:
                    name = getSafeName(res.name)
                else:
                    name = res.name
                
                if count > 0:
                    name = '%s_%d' % (name, count)
                resource_name_dict[resource_id] = name

    return resource_name_dict[resource_id]

def generate_raw_data(controller):
    print('^generate_raw_data')
    # Start iterating from the first real draw as a child of markers
    # draw type = DrawcallDescription
    global API_TYPE
    api_prop = controller.GetAPIProperties()
    API_TYPE = api_prop.pipelineType
    print('API_TYPE', API_TYPE)

    draws = controller.GetDrawcalls()
    draw = draws[0]

    while len(draw.children) > 0:
        draw = draw.children[0]

    # Iterate over all of the root drawcalls
    for d in draws:
        visit_draw(controller, d)

    print('$generate_raw_data')

def generate_derived_data(controller):

    print('^generate_derived_data')
    
    print('$generate_derived_data')


def generate_viz(controller): 
    print('^generate_viz')
    g_frame.writeIndexHtml(index_html, controller)

    for p in g_frame.passes:
        p.writeDetailHtml(controller)
  
    g_frame.exportResources(controller)
    print('$generate_viz')
    print("%s\n" % (report_name))

def print_var(v, indent = '', shader_name = '', setup_shader_doctor = False):
    # TODO: ugly
    if '[' in v.name or ']' in v.name:
        # v is a row of a matrix
        valstr = ''
        indent = ''
    else:
        if setup_shader_doctor:
            g_frame.shaders[shader_name]['uniforms'][v.name] = {
                'used': False
            }
        valstr = indent + v.name + "\n"

    if len(v.members) == 0:
        # leaf node
        for r in range(0, v.rows):
            valstr += indent + '  '

            for c in range(0, v.columns):
                if v.type == rd.VarType.Float:
                    valstr += '%.3f ' % v.value.f32v[r*v.columns + c]
                elif v.type == rd.VarType.Double:
                    valstr += '%.3g ' % v.value.f64v[r*v.columns + c]
                elif v.type == rd.VarType.SInt:
                    valstr += '%d ' % v.value.s32v[r*v.columns + c]
                elif v.type == rd.VarType.UInt:
                    valstr += '%d ' % v.value.u32v[r*v.columns + c]

            if r < v.rows-1:
                valstr += "\n"

    for v in v.members:
        valstr += print_var(v, indent + '    ')

    valstr += '\n'

    return valstr

def get_cbuffer_contents(controller, stage, shader_name, refl, program_name):
    pipe = controller.GetPipelineState()

    contents = ''

    pso = pipe.GetGraphicsPipelineObject()
    if stage == rd.ShaderStage.Compute:
        pso = pipe.GetComputePipelineObject()

    shader = pipe.GetShader(stage)

    setup_shader_doctor = False
    if shader not in g_frame.shaders:
        setup_shader_doctor = True
        g_frame.shaders[shader_name] = {
            'state': program_name,
            'type': ShaderStage(stage).name,
            'uniforms': {}
        }

    if API_TYPE != rd.GraphicsAPI.OpenGL:
        setup_shader_doctor = False

    for slot in range(0, 4):
        cb = pipe.GetConstantBuffer(stage, slot, 0)

        cbufferVars = controller.GetCBufferVariableContents(pso,
                                                            pipe.GetShader(stage),
                                                            pipe.GetShaderEntryPoint(stage), slot,
                                                            cb.resourceId, cb.byteOffset, cb.byteSize)

        if not cbufferVars:
            break

        for v in cbufferVars:
            contents += print_var(v, shader_name = shader_name, setup_shader_doctor = setup_shader_doctor)
        contents += '\n----------------------------------\n'

    if setup_shader_doctor:
        rawBytes = str(refl.rawBytes, 'utf-8')
        for k,v in g_frame.shaders[shader_name]['uniforms'].items():
            if rawBytes.count(k) > 1:
                # uniform definition itself cost one occurence
                v['used'] = True

    return contents

def fetch_gpu_counters(controller):
    global g_draw_durations
    counter_type = rd.GPUCounter.EventGPUDuration
    results = controller.FetchCounters([counter_type])
    counter_desc = controller.DescribeCounter(counter_type)

    for r in results:
        id = r.eventId

        if counter_desc.resultByteWidth == 4:
            val = r.value.f
        else:
            val = r.value.d

        g_draw_durations[id] = val

def rdc_main(controller):
    global g_assets_folder
    global report_name
    global index_html
    global WRITE_TEXTURE, WRITE_DEPTH_BUFFER, WRITE_MALIOC
    global api_full_log, api_short_log

    try:
        api_full_log = open(g_assets_folder / 'api_full.txt',"w") 
        api_short_log = open(g_assets_folder / 'api_short.txt',"w") 

        report_name = g_assets_folder / 'index.html'
        if 'atelier' in g_assets_folder.stem:
            # WAR: make specific reports smaller
            WRITE_TEXTURE = False

        fetch_gpu_counters(controller)
        generate_raw_data(controller)
        generate_derived_data(controller)

        index_html = open(report_name,"w") 
        generate_viz(controller)

        api_full_log.close()
        api_short_log.close()
    except Exception as e:
        print(str(e))

def shutdown_rdc(cap, controller):
    controller.Shutdown()
    cap.Shutdown()
    rd.ShutdownReplay()

if 'pyrenderdoc' in globals():
    rdc_file = pyrenderdoc.GetCaptureFilename()
    absolute = WindowsPath(rdc_file).absolute()
    g_assets_folder = absolute.parent / absolute.stem
    if False:
        from datetime import datetime
        g_assets_folder = g_assets_folder + '-' + datetime.now().strftime("%Y-%b-%d-%H-%M-%S")
    g_assets_folder.mkdir(parents=True, exist_ok=True)
    
    pyrenderdoc.Replay().BlockInvoke(rdc_main)
else:
    if len(sys.argv) > 1:
        rdc_file = sys.argv[1]
    absolute = WindowsPath(rdc_file).absolute()
    g_assets_folder = absolute.parent / absolute.stem
    g_assets_folder.mkdir(parents=True, exist_ok=True)

    cap, controller = setup_rdc(rdc_file)
    rdc_main(controller)
    shutdown_rdc(cap, controller)
