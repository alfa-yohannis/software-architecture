FROM maven:3.9.6-eclipse-temurin-17 as build

WORKDIR /workspace/app

#COPY performance/mvnw .
#COPY performance/.mvn .mvn
COPY performance/pom.xml .
COPY performance/src src

RUN mvn install -DskipTests
RUN mkdir -p target/dependency && (cd target/dependency; jar -xf ../*.jar)

FROM maven:3.9.6-eclipse-temurin-17
EXPOSE 8081
VOLUME /tmp
ARG DEPENDENCY=/workspace/app/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
ENTRYPOINT ["java","-cp","app:app/lib/*","software.architecture.microservice.PerformanceServiceApplication"]
