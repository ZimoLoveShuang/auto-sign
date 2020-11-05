from config import ROOT_PATH_CONFIG_USER, TITLE


def refresh_database(file_path: str = None, token: str = 'none', purview: str = 'read'):
    """

    :param purview: read or write
    :param file_path: file format:csv
    :param token:
    :return:
    """
    import csv
    if file_path is None:
        file_path = ROOT_PATH_CONFIG_USER

    new_data = dict()

    def read_data(data_format='new'):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = [i for i in csv.reader(f)]
        title = reader[0]
        data = reader[1:]
        for i in range(data.__len__()):
            if data[i].__len__() < title.__len__():
                temp_docker = (title.__len__() - data[i].__len__()) * [token]
                data[i] += temp_docker
            new_data.update(
                {data[i][0]: dict(zip(TITLE, data[i]))}
            )
        if data_format == 'new':
            return new_data

    def write_data(data_flow=None):
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(TITLE)

            if data_flow:
                for data in data_flow:
                    writer.writerow(data)

    if purview == 'read':
        return read_data(data_format='new')
    else:
        write_data(read_data())
