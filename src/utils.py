import pandas as pd


def df_sensor_msg_freq(df: pd.DataFrame, ip_address: str, mqtt_msgtype: float) -> pd.DataFrame:
    """
    Filters df for packets of a given sensor IP address and mqtt.msgtype.
    :param df: df of normal packets.
    :param ip_address: sensor IP address.
    :param mqtt_msgtype: MQTT message type corresponding to Wireshark convention.
    :return: df with only packets of mqtt_msgtype for the given sensor IP address.
    """
    df_copy = df.copy()

    df_copy = df_copy[df_copy["ip.src"] == ip_address]
    df_copy = df_copy[df_copy["mqtt.msgtype"] == mqtt_msgtype]
    df_copy = df_copy.sort_values("frame.time_epoch")
    df_copy["delta"] = df_copy["frame.time_epoch"].diff()

    return df_copy