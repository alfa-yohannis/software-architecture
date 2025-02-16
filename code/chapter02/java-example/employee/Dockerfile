FROM maven:3.9.6-eclipse-temurin-17 as build

WORKDIR /workspace/app

COPY pom.xml .
COPY src src

RUN mvn install -DskipTests
RUN mkdir -p target/dependency && (cd target/dependency; jar -xf ../*.jar)

COPY application.properties target/dependency

FROM maven:3.9.6-eclipse-temurin-17
EXPOSE 8080
#VOLUME /tmp
ARG DEPENDENCY=/workspace/app/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
COPY --from=build ${DEPENDENCY}/application.properties /app
ENTRYPOINT ["java","-cp","app:app/lib/*","software.architecture.microservice.EmployeeServiceApplication"]
