FROM rocker/tidyverse:latest

# Install R packages
RUN apt-get -y install libtiff5-dev
RUN install2.r --error \
    fs \
    imager \
    argparser \
    reshape2 \
    Xmisc
