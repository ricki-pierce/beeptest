import asyncio
import xml.etree.ElementTree as ET

import qtm

def create_body_index(xml_string):
    """ Extract a name to index dictionary from 6dof settings xml """
    xml = ET.fromstring(xml_string)

    body_to_index = {}
    for index, body in enumerate(xml.findall("*?Body?Name")):
        body_to_index[body.text.strip()] = index

    return body_to_index


async def main():

    # Connect to qtm
    connection = await qtm.connect("127.0.0.1")

    #Connection failed?
    if connection is None:
        print("Failed to connect")
        return
    
    # Take control of qtm, context manager will automatically release control after scope end
    async with qtm.take_control(connection, "password"):

        realtime = False

        if realtime:
            #Start new realtime
            await connection.new()
        else:
            #Load qtm file
            await connection.load("C:/Users/Ricki/project.qtm")

            #start rtfromfile
            await connection.start(rtfromfile=True)

    # get 6dof settings from qtm
    xml_string = await connection.get_parameters(parameters=["6d"])
    body_index = create_body_index(xml_string)

    wanted_body = "Ball"