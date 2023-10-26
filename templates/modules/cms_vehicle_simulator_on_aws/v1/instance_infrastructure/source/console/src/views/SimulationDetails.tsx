// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from "react";
import { redirect, useLocation } from "react-router-dom";
import { I18n, Logger } from "@aws-amplify/core";
import { API_NAME } from "../util/Utils";
import {
  ISimDetailsProps,
  ISimulation,
  simTypes,
} from "../components/Shared/Interfaces";
import { API } from "@aws-amplify/api";
import moment from "moment";
import PageTitleBar from "../components/Shared/PageTitleBar";
import Footer from "../components/Shared/Footer";
import Card from "react-bootstrap/Card";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Tab from "react-bootstrap/Tab";
import Nav from "react-bootstrap/Nav";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";

import {
  CONNECTION_STATE_CHANGE,
  ConnectionState,
  PubSub,
} from "@aws-amplify/pubsub";
import { Hub } from "aws-amplify";

export default function SimulationDetails(
  props: ISimDetailsProps
): React.JSX.Element {
  const location = useLocation();
  const logger = new Logger("Simulation Details");
  const [sim, setSim] = useState<ISimulation>();
  const [topics, setTopics] = useState<{ [key: string]: Array<string> }>({});
  const [messages, setMessages] = useState<Array<any>>([]);
  const [activeTopic, setActiveTopic] = useState<string>();
  const [activeDevice, setActiveDevice] = useState<{ [key: string]: string }>({
    id: "All",
    name: "All",
  });

  /**
   * Load simulation from ddb
   */
  const loadSimulation = async () => {
    const sim_id = location.pathname.split("/").pop();
    try {
      const results = await API.get(API_NAME, `/simulation/${sim_id}`, {});
      setSim(results);
    } catch (err: any) {
      logger.error(I18n.get("simulation.get.error"), err);
      if (err.response?.data?.error === "MissingSimulation") {
        redirect("/404");
      } else {
        throw err;
      }
    }
  };

  /**
   * load devices belonging to a simulation
   */
  const loadDevices = async () => {
    const sim_id = location.pathname.split("/").pop();
    try {
      const results = await API.get(API_NAME, `/simulation/${sim_id}`, {
        queryStringParameters: {
          op: "list dtype attributes",
          filter: "topic, type_id",
        },
      });
      let newTopics: { [key: string]: Array<string> } = {};

      results.devices.forEach((result: any) => {
        for (let i = 0; i < result.amount; i++) {
          const topicName = `${props.topicPrefix}/${result.name}-${i}`;
          if (!newTopics[topicName]) {
            newTopics[topicName] = [result.type_id];
          } else {
            newTopics[topicName].push(result.type_id);
          }
        }
      });

      setTopics({ ...newTopics });
      setActiveTopic(Object.keys(newTopics)[0]);
    } catch (err) {
      logger.error(I18n.get("device.types.get.error"), err);
      throw err;
    }
  };

  /**
   * parse and save incoming IoT message
   * @param data
   */
  const handleMessage = (data: any) => {
    let message = {
      title: data.value[Object.getOwnPropertySymbols(data.value)[0]],
      content: data.value,
      timestamp: moment().format("MMM Do YYYY HH:mm:ss"),
    };
    if (messages.length >= 100) {
      messages.pop();
    }
    messages.unshift(message);
    setMessages([...messages]);
  };

  /**
   * react useEffect hook
   * load simulation and needed device type info (topic, id) on load
   * and initializes map if auto demo
   */
  useEffect(() => {
    loadSimulation();
    loadDevices();
  }, []);

  /**
   * updates the map coordinates with new messages if a map exists
   */

  /**
   * react useEffect hook
   * on topics changes subscribe and unsubscribe.
   */
  useEffect(() => {
    const iotSub = PubSub.subscribe(Object.keys(topics)).subscribe({
      next: (data: any) => {
        handleMessage(data);
      },
      error: (error: any) => {
        logger.error(error);
      },
    });
    Hub.listen("pubsub", (data: any) => {
      const { payload } = data;
      if (payload.event === CONNECTION_STATE_CHANGE) {
        const connectionState = payload.data.connectionState as ConnectionState;
        console.log(connectionState);
      }
    });
    return () => {
      iotSub.unsubscribe();
    };
  }, [topics]);

  /**
   * start simulation
   */
  const startSim = async () => {
    if (sim && sim.stage === "sleeping") {
      const body = {
        action: "start",
        simulations: [sim],
      };
      try {
        await API.put(API_NAME, `/simulation/${sim.sim_id}`, { body: body });
        sim.stage = "running";
        setSim({ ...sim });
      } catch (err) {
        logger.error(I18n.get("simulation.start.error"), err);
        throw err;
      }
    }
  };

  /**
   * stop simulation
   */
  const stopSim = async () => {
    if (sim && sim.stage === "running") {
      const body = {
        action: "stop",
        simulations: [sim],
      };
      try {
        await API.put(API_NAME, `/simulation/${sim.sim_id}`, { body: body });
        sim.stage = "stopping";
        setSim({ ...sim });
      } catch (err) {
        logger.error(I18n.get("simulation.stop.error"), err);
        throw err;
      }
    }
  };

  return (
    <div className="page-content">
      <PageTitleBar title={props.title} />
      <Card className="content-card">
        <Card.Title className="content-card-title">
          {sim?.name}
          <Button
            className="button-theme header-button"
            size="sm"
            onClick={() => {
              loadSimulation();
            }}
          >
            <i className="bi bi-arrow-repeat" /> {I18n.get("refresh")}
          </Button>
          <Button
            className="button-theme-alt header-button mr-3"
            style={{ marginRight: "1rem" }}
            size="sm"
            onClick={() => {
              stopSim();
            }}
          >
            <i className="bi bi-stop-fill" /> {I18n.get("stop")}
          </Button>
          <Button
            className="button-theme header-button"
            size="sm"
            onClick={() => {
              startSim();
            }}
          >
            <i className="bi bi-play-fill" /> {I18n.get("start")}
          </Button>
        </Card.Title>
        <Card.Body>
          <Row>
            <Col sm="6">
              <Row className="detail">
                <Col sm="3">
                  <b>{I18n.get("name")}:</b>
                </Col>
                <Col sm="9">{sim?.name}</Col>
              </Row>
              <Row className="detail">
                <Col sm="3">
                  <b>{I18n.get("stage")}:</b>
                </Col>
                <Col sm="9">{sim?.stage}</Col>
              </Row>
              <Row className="detail mb-0">
                <Col sm="3">
                  <b>{I18n.get("created")}:</b>
                </Col>
                <Col sm="9">{sim?.created_datetime}</Col>
              </Row>
            </Col>
            <Col sm="6">
              <Row className="detail">
                <Col sm="3">
                  <b>{I18n.get("runs")}:</b>
                </Col>
                <Col sm="9">{sim?.runs}</Col>
              </Row>
              <Row className="detail">
                <Col sm="3">
                  <b>{I18n.get("last.run")}:</b>
                </Col>
                <Col sm="9">{sim?.last_run}</Col>
              </Row>
              <Row className="detail mb-0">
                <Col sm="3">
                  <b>{I18n.get("last.updated")}:</b>
                </Col>
                <Col sm="9">{sim?.updated_datetime}</Col>
              </Row>
            </Col>
          </Row>
        </Card.Body>
      </Card>
      {sim?.sim_id.includes(simTypes.autoDemo) ? (
        <div className="map" id="map" />
      ) : (
        ""
      )}
      <Card className="mt-3">
        <Card.Header>
          <Card.Title>
            <Row>
              <Col sm={3}>{I18n.get("topic")}</Col>
              <Col sm={9}>
                <Row>
                  <Col>{I18n.get("messages")}</Col>
                  <Col>
                    <DropdownButton
                      className="float-right"
                      variant="outline-secondary"
                      title={`Device Filter: ${activeDevice.name} `}
                      id="input-group-dropdown-2"
                    >
                      <Dropdown.Item
                        key={-1}
                        href="#"
                        onClick={() =>
                          setActiveDevice({ id: "All", name: "All" })
                        }
                      >
                        {I18n.get("all")}
                      </Dropdown.Item>
                      {sim?.devices.map((device, i) => {
                        if (
                          activeTopic &&
                          topics[activeTopic].includes(device.type_id)
                        ) {
                          let items = [];
                          for (let j = 0; j < device.amount; j++) {
                            items.push(`${device.name}-${j}`);
                          }
                          const prefix = `${sim.sim_id.slice(
                            0,
                            3
                          )}${device.type_id.slice(0, 3)}`;
                          return items.map((item, k) => (
                            <Dropdown.Item
                              key={`${item}-${i}-${k}`}
                              href="#"
                              onClick={() =>
                                setActiveDevice({
                                  id: `${prefix}${k}`,
                                  name: `${item}`,
                                })
                              }
                            >
                              {item}
                            </Dropdown.Item>
                          ));
                        }
                      })}
                    </DropdownButton>
                  </Col>
                </Row>
              </Col>
            </Row>
          </Card.Title>
        </Card.Header>
        <Card.Body>
          <Tab.Container id="left-tabs-example" defaultActiveKey={"0"}>
            <Row>
              <Col sm={3}>
                <Nav variant="pills" className="flex-column topic-content">
                  {Object.keys(topics).map((topic, i) => (
                    <Nav.Item className="topic-item" key={`${topic}-${i}`}>
                      <Nav.Link
                        eventKey={i}
                        onClick={() => {
                          setActiveTopic(topic);
                          setActiveDevice({ id: "All", name: "All" });
                        }}
                      >
                        {topic}
                      </Nav.Link>
                    </Nav.Item>
                  ))}
                </Nav>
              </Col>
              <Col sm={9} className="message-content">
                <Tab.Content>
                  {Object.entries(topics).map((aTopic, i) => (
                    <Tab.Pane key={`${aTopic.join()}-${i}`} eventKey={i}>
                      {messages
                        .filter((message) =>
                          activeDevice.id === "All"
                            ? message.title === aTopic[0]
                            : message.title === aTopic[0] &&
                              message.content["_id_"] === activeDevice.id
                        )
                        .map((message, j) => (
                          <Card key={`${message.title}-${j}`} className="mb-4">
                            <Card.Title className="content-card-title pl-2 pt-2">
                              {message.timestamp}
                            </Card.Title>
                            <Card.Body className="iot-message-card">
                              <pre>
                                {JSON.stringify(message.content, null, 2)}
                              </pre>
                            </Card.Body>
                          </Card>
                        ))}
                    </Tab.Pane>
                  ))}
                </Tab.Content>
              </Col>
            </Row>
          </Tab.Container>
        </Card.Body>
      </Card>
      <Footer pageTitle={props.title} />
    </div>
  );
}
