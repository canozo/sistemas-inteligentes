cmake_minimum_required(VERSION 3.1)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -lsqlite3")

add_executable(
  main.exe
  src/main.c
  src/bucket.c
)
