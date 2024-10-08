FROM nvidia/cuda:12.0.0-devel-ubuntu20.04

# Variables
ENV CL_API_URL="https://api.btcpuzzle.info"
ENV CL_USER_TOKEN="xyz"
ENV CL_WALLET_ADDRESS = "1EEq7exE91EUCLvC5s6PeecPmUomwA7GMy"
ENV CL_API_SENDER = ""
ENV CL_TARGET="1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
ENV CL_PREFIX="00000000000000000000000000000000000000000000000"
ENV CL_PUZZLE_CODE = "67"
ENV CL_START_WITH = "64"
ENV CL_GPU_ID = "0"

ENV VANITYCCAP=2.0

WORKDIR /app
RUN apt-get update \
 && apt-get install git nano curl -y

# Clone and build vanitysearch.
WORKDIR /app
RUN git clone https://github.com/albertodst/VanitySearch.git
WORKDIR /app/VanitySearch