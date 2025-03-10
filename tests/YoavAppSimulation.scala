package io.gatling.app

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

class YoavAppSimulation extends Simulation {

  val baseUrl = "http://localhost:8080/yoavlav-devopscourse"

  val httpProtocol = http
    .baseUrl(baseUrl)
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .userAgentHeader("Gatling Load Test")

  val scn = scenario("Yoav's App Basic Test")
    .exec(
      http("Load Home Page")
        .get("/")
        .check(status.is(200))
    )
    .pause(1) // simulate user think time
    .exec(
      http("Load About Page")
        .get("/about.jsp")
        .check(status.is(200))
    )

  // Get test type from command line (default is "load")
  val testType = System.getProperty("testType", "load")

  val injectionProfile = testType match {
    case "max" =>
      println("Running MAX USER TEST: 200 users ramped over 2 minutes")
      scn.inject(
        rampUsers(200).during(2.minutes)
      )

    case "load" =>
      println("Running LOAD TEST: 50 users/sec for 5 minutes")
      scn.inject(
        constantUsersPerSec(50).during(5.minutes)
      )

    case "stress" =>
      println("Running STRESS TEST: Ramp from 10 to 200 users/sec over 4 minutes")
      scn.inject(
        rampUsersPerSec(10).to(200).during(4.minutes)
      )

    case _ =>
      println("Unknown test type. Defaulting to LOAD TEST.")
      scn.inject(
        constantUsersPerSec(50).during(5.minutes)
      )
  }

  setUp(
    injectionProfile
  ).protocols(httpProtocol)
}