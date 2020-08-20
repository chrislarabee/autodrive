

class Column:
    """
    Organizes defaults and validation for a column in a spreadsheet.
    """
    def __init__(self, dtype=str, default=None):
        """

        :param dtype: A string, which must be one of the valid_dtypes.
        :param default: A default value to use when a row in the
            spreadsheet has no value for this Column. Must be of a
            data type that matches dtype.
        """
        valid_dtypes = ['any', str, int, bool, list, float]
        if dtype not in valid_dtypes:
            raise ValueError(f'Invalid dtype: {dtype}')
        self.dtype = dtype
        # Check if the passed default matches the Column's dtype.
        if not self._validate(default):
            raise ValueError(f'Default value does not match dtype: {default}')
        self.default = default

    def _validate(self, val):
        """
        Takes a value and makes sure it is of the same data type as
        self.dtype.

        :param val: An object.
        :return: A boolean indicating if the passed object matches
            self.dtype.
        """
        if val is None:
            return True
        else:
            return isinstance(val, self.dtype)


class Schema:
    """
    Organizes data rules (schema) for each spreadsheet in the google
    sheet and allows incoming data to be morphed to fit the schema
    of the sheet it came from.
    """

    def __init__(self, **kwargs):
        """

        :param kwargs: Key-value pairs where the value must be a
            string, list/tuple, or None (other object types are
            treated as None), which will be converted into a Column
            object.
        """
        for k, v in kwargs.items():
            if isinstance(v, list) or isinstance(v, tuple):
                c = Column(v[0], v[1])
            elif v is None:
                c = Column()
            else:
                c = Column(v)
            setattr(self, k, c)

    @staticmethod
    def _bool(val):
        """
        This is basically just a version of python's bool that actually
        converts the string to a boolean type correctly.

        :param val: A string.
        :return: val as a boolean, if convertible.
        """
        if val == 'FALSE':
            result = False
        elif val == 'TRUE':
            result = True
        else:
            raise ValueError(f'Cannot convert {val} to bool')
        return result

    @staticmethod
    def _convert(val, data_type):
        """
        Takes a string and a target data_type and attempts to convert it.

        :param val: A string.
        :param data_type: An object in [float, int, bool, 'any'].
        :return: The converted val, or the original val if conversion failed.
        """
        if data_type == 'any':
            for f in [int, float, Schema._bool]:
                result, output_val = Schema._try_convert(val, f)
                if result:
                    break
        elif data_type == bool:
            result, output_val = Schema._try_convert(val, Schema._bool)
        else:
            result, output_val = Schema._try_convert(val, data_type)
        return output_val

    @staticmethod
    def _try_convert(val, func):
        """
        Takes a string and uses func to try and convert it.
        :param val: A string.
        :param func: A data type conversion function.
        :return: A boolean indicating whether the conversion
            succeeded and either val or the converted val if
            successful.
        """
        if val is None:
            raise TypeError('_try_convert cannot accept None val.')
        try:
            result = func(val)
        except ValueError:
            return False, val
        else:
            return True, result

    def parse(self, row_dict):
        """
        Takes a piece of data (row_dict) and makes sure that it has all
        the keys in the currently selected schema. Applies schema rules
        to all values present in the data.
        """
        output_dict = {}
        for key, col in self.__dict__.items():
            data_type = col.dtype
            default = col.default
            if key in row_dict.keys():
                val = row_dict[key]
                if val == '':
                    output_val = default
                else:
                    if data_type == list:
                        output_val = val.split(',')
                    elif data_type == str:
                        output_val = val
                    else:
                        output_val = Schema._convert(val, data_type)
                output_dict[key] = output_val
            else:
                output_dict[key] = default

        return output_dict
