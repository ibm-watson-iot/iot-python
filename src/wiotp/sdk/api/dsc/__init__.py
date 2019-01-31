# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.dsc.connectors import Connectors as DSC

"""
General overview of how DSC stuff ties together:

- 1. Set up one or more services (e.g. link a Cloudant account `/s2s/services`)
- 2. Configure a connector by defining one or more forwarding rules and destinations (`/historianconnectors`)
- 2a. Configure one or more destinations in services (e.g. a database in your Cloudant account `historianconnectors/%s/destinations`)
- 2b. Set up one or more forwarding rules, each to one or more destinations (e.g. route certain events to a database in Cloudant `historianconnectors/%s/forwardingrules`)

"""
