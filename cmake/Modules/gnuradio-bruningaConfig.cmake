find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_BRUNINGA gnuradio-bruninga)

FIND_PATH(
    GR_BRUNINGA_INCLUDE_DIRS
    NAMES gnuradio/bruninga/api.h
    HINTS $ENV{BRUNINGA_DIR}/include
        ${PC_BRUNINGA_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_BRUNINGA_LIBRARIES
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

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-bruningaTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_BRUNINGA DEFAULT_MSG GR_BRUNINGA_LIBRARIES GR_BRUNINGA_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_BRUNINGA_LIBRARIES GR_BRUNINGA_INCLUDE_DIRS)
