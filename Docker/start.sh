#!/bin/sh

export USER_TOKEN="${CL_USER_TOKEN}"
export START_WITH="${CL_START_WITH}"
export WALLET_ADDRESS="${CL_WALLET_ADDRESS}"
export API_SENDER="${CL_API_SENDER}"
export TARGET="${CL_TARGET}"
export PUZZLE_CODE="${CL_PUZZLE_CODE}"
export GPU_ID="${CL_GPU_ID}"

/usr/bin/python3 index.py