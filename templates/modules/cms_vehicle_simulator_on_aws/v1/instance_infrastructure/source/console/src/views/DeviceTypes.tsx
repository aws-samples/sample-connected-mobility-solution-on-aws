// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

import { I18n, Logger } from "@aws-amplify/core";
import { API } from "@aws-amplify/api";
import { API_NAME } from "../util/Utils";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageTitleBar from "../components/Shared/PageTitleBar";
import DeleteConfirm from "../components/Shared/DeleteConfirmation";
import Footer from "../components/Shared/Footer";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";
import { IDeviceType, IPageProps } from "../components/Shared/Interfaces";

export default function DeviceTypes(props: IPageProps): JSX.Element {
  const logger = new Logger("Device Types");
  const [deviceTypes, setDeviceTypes] = useState<IDeviceType[]>([]);
  const [showAlert, setShowAlert] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  /**
   * retrieves device types and sets to state
   */
  const loadDeviceTypes = async () => {
    try {
      const results = await API.get(API_NAME, "/device/type", {});
      setDeviceTypes([...results]);
    } catch (err) {
      logger.error(I18n.get("device.type.get.error"), err);
      throw err;
    }
  };

  /**
   * deletes device type from dynamodb and reloads the page
   * @param type_id
   */
  const handleDelete = async (type_id: string, index: number) => {
    try {
      await API.del(API_NAME, `/device/type/${type_id}`, {});
      deviceTypes.splice(index, 1);
      setDeviceTypes([...deviceTypes]);
    } catch (err) {
      logger.error(I18n.get("device.type.delete.error"), err);
      throw err;
    }
  };

  /**
   * React useEffect hook
   * retrieves the device types from dynamodb
   */
  useEffect(() => {
    loadDeviceTypes();
  }, []);

  /** React useEffect hook
   * sets showAlert on deviceTypes changes
   */
  useEffect(() => {
    setShowAlert(deviceTypes.length === 0);
  }, [deviceTypes]);

  /**
   * Populates a table row for each device type
   * @returns table row per device type
   */
  const displayDeviceTypes = () => {
    if (deviceTypes) {
      return deviceTypes.map((dtype, i) => (
        <tr key={`${dtype.type_id}-${i}`}>
          <td></td>
          <td>{dtype.name}</td>
          <td>{dtype.topic}</td>
          <td>{dtype.created_datetime}</td>
          <td>{dtype.updated_datetime}</td>
          <td>
            <Link
              to={`/device/type/${dtype.type_id}`}
              state={{
                originalDeviceType: dtype,
              }}
            >
              <Button className="button-theme" size="sm">
                <i className="bi bi-pencil-fill" /> {I18n.get("edit")}
              </Button>
            </Link>
            <Button
              className="button-theme-alt"
              size="sm"
              onClick={() => {
                setShowDeleteModal(true);
              }}
            >
              <i className="bi bi-trash-fill" /> {I18n.get("delete")}
            </Button>
            <DeleteConfirm
              id={dtype.type_id}
              name={dtype.name}
              delete={handleDelete}
              showModal={setShowDeleteModal}
              show={showDeleteModal}
              index={i}
            />
          </td>
        </tr>
      ));
    }
  };

  /**
   * Creates an alert if there are no device types to display
   */
  const emptyDeviceTypeAlert = () => {
    return (
      <Alert className="empty-alert" variant="secondary" show={showAlert}>
        <Alert.Heading>{I18n.get("no.device.types")}</Alert.Heading>
        <a href="/device/type/create">{I18n.get("create.device.type")}</a>&nbsp;
        {I18n.get("to.get.started")}
      </Alert>
    );
  };

  return (
    <div className="page-content">
      <PageTitleBar title={props.title} />
      <Row>
        <Col>
          <Card className="content-card">
            <Card.Title className="content-card-title">
              {I18n.get("device.types")} ({deviceTypes ? deviceTypes.length : 0}
              )
              <Button
                className="button-theme header-button"
                size="sm"
                onClick={() => {
                  loadDeviceTypes();
                }}
              >
                <i className="bi bi-arrow-repeat" /> {I18n.get("refresh")}
              </Button>
              <Button
                href="/device/type/create"
                size="sm"
                className="button-theme header-button"
              >
                <i className="bi bi-plus" /> {I18n.get("device.type.add")}
              </Button>
            </Card.Title>
            <Card.Body className="content-card-body">
              <Table className="content-card-table" hover>
                <thead className="table-header">
                  <tr>
                    <th></th>
                    <th>{I18n.get("device.types")}</th>
                    <th>{I18n.get("topic")}</th>
                    <th>{I18n.get("created")}</th>
                    <th>{I18n.get("last.updated")}</th>
                    <th>{I18n.get("actions")}</th>
                  </tr>
                </thead>
                <tbody>{displayDeviceTypes()}</tbody>
              </Table>
              {emptyDeviceTypeAlert()}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      <Footer pageTitle={props.title} />
    </div>
  );
}
