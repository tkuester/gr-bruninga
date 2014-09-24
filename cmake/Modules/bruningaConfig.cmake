INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_BRUNINGA bruninga)

FIND_PATH(
    BRUNINGA_INCLUDE_DIRS
    NAMES bruninga/api.h
    HINTS $ENV{BRUNINGA_DIR}/include
        ${PC_BRUNINGA_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    BRUNINGA_LIBRARIES
    NAMES gnuradio-bruninga
    HINTS $ENV{BRUNINGA_DIR}/lib
        ${PC_BRUNINGA_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(BRUNINGA DEFAULT_MSG BRUNINGA_LIBRARIES BRUNINGA_INCLUDE_DIRS)
MARK_AS_ADVANCED(BRUNINGA_LIBRARIES BRUNINGA_INCLUDE_DIRS)

