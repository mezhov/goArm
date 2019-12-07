class goArmConsts:
    # commands server receives from cam/admin interface
    com_Problem = 'P'  # P <level>
    com_TeachMe = 'TEACH'
    com_Play = 'PLAY'  # PLAY B|W|""
    com_Fin = 'FIN'
    com_Calib = "CALIB"
    com_ACTIONS = [com_Problem, com_TeachMe, com_Play, com_Fin, com_Calib]

    # commands server sends to camera
    com_Snap = 'SNAP'
    com_Disconnect = 'Disconnect'
    com_HOLD = 'HOLD'
    com_RESUME = 'RESUME'
    com_Bowl = 'BOWL'  # BOWL B|W - to locate stones in a bowl of certain color
    com_LED = 'LED'  # LED <color> ON|OFF

    msg_t_RESPONSE = 1
    msg_t_REQUEST = 2

    msg_OK = 'OK'
    msg_NOT_IMPLEMENTED = 'COMMAND_NOT_IMPLEMENTED'
    msg_UNKNOWN = 'UNKNOWN_COMMAND'
