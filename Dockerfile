FROM cae-artifactory.jpl.nasa.gov:17001/node:22.14.0
WORKDIR /app
COPY . /app
RUN npm ci && \
	mkdir /app/data
USER root
ENTRYPOINT ["npm", "start"]
