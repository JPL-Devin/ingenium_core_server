FROM cae-artifactory.jpl.nasa.gov:17001/node:12.22.1
WORKDIR /app
COPY . /app
RUN npm ci && \
	mkdir /app/data
USER root
ENTRYPOINT ["npm", "start"]
