// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

/*
 * Copyright 2022 The Backstage Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { createBackendModule } from "@backstage/backend-plugin-api";
import { catalogProcessingExtensionPoint } from "@backstage/plugin-catalog-node/alpha";
import { PartnerOfferingEntitiesProcessor } from "./processor";

/**
 * Registers support for the partner offering specific entity model (e.g. the Partner Offering
 * kind) to the catalog backend plugin.
 *
 * @public
 */
export const partnerOfferingEntityModel = createBackendModule({
  pluginId: "catalog",
  moduleId: "acdp-partner-offering-backend",
  register(env) {
    env.registerInit({
      deps: {
        catalog: catalogProcessingExtensionPoint,
      },
      async init({ catalog }) {
        catalog.addProcessor(new PartnerOfferingEntitiesProcessor());
      },
    });
  },
});
