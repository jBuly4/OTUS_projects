import pytest

import apiscoring.api

class TestField:
    @pytest.mark.parametrize(
            'value, required, nullable, field_type, exception',
            [
                (None, True, True, type(None), ValueError),
                (None, True, False, type(None), ValueError),
                ('', False, False, str, ValueError),
                ([], False, False, list, ValueError),
            ]
    )
    def test_none_valid_field(self, value, required, nullable, field_type, exception):
        field = apiscoring.api.Field(required=required, nullable=nullable)
        field.value = value

        with pytest.raises(exception):
            field.validate_field(field_type=field_type)

    @pytest.mark.parametrize(
            'value, required, nullable, field_type',
            [
                (0, True, True, int),
                (None, False, True, type(None)),
                ('', True, True, str),
                ([], True, True, list),
                ((0, '0'), False, False, tuple),
            ]
    )
    def test_valid_field(self, value, required, nullable, field_type):
        field = apiscoring.api.Field(required=required, nullable=nullable)
        field.value = value

        assert field.validate_field(field_type)


class TestCharField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
            ]
    )
    def test_none_valid_char_field(self, value, exception):
        char_field = apiscoring.api.CharField(required=False, nullable=True)
        char_field.value = value

        with pytest.raises(exception):
            char_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                'a',
                'some@mail.tut',
                'randomstr37840ing',
            ]
    )
    def test_valid_char_field(self, value):
        char_field = apiscoring.api.CharField(required=False, nullable=True)
        char_field.value = value

        assert char_field.validate_field()


class TestEmailField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', ValueError),
                ('12344', ValueError),
                ('ad!#()ads@@@@1111aw21.ru', ValueError)
            ]
    )
    def test_none_valid_email_field(self, value, exception):
        email_field = apiscoring.api.EmailField(required=False, nullable=True)
        email_field.value = value

        with pytest.raises(exception):
            email_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                'a@opa.tr',
                'some@mail.tut',
                'randomstr37840ing@test.com',
                'many-specia1_character3@pro.pro',
            ]
    )
    def test_valid_email_field(self, value):
        email_field = apiscoring.api.EmailField(required=False, nullable=True)
        email_field.value = value

        assert email_field.validate_field()


class TestPhoneField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, ValueError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', ValueError),
                ('12344', ValueError),
                ('7tencharups', ValueError),
                (89992223535, ValueError),
                (7, ValueError),
                ('89992223535', ValueError),
            ]
    )
    def test_none_valid_phone_field(self, value, exception):
        phone_field = apiscoring.api.PhoneField(required=False, nullable=True)
        phone_field.value = value

        with pytest.raises(exception):
            phone_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                '71111111111',
                71111111111,
                71234567891,
                '71234567891',
                '77777777777',
                77777777777,
            ]
    )
    def test_valid_phone_field(self, value):
        phone_field = apiscoring.api.PhoneField(required=False, nullable=True)
        phone_field.value = value

        assert phone_field.validate_field()


class TestDateField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', ValueError),
                ('some.another.string', ValueError),
                ('1.2.3', ValueError),
                ('198.162.1.22', ValueError),
                ('01.01.22', ValueError),
                ('32.12.2022', ValueError),
                ('45.05.2005', ValueError),
                ('01/01/2022', ValueError),
                ('99.99.9999', ValueError),
            ]
    )
    def test_none_valid_date_field(self, value, exception):
        date_field = apiscoring.api.DateField(required=False, nullable=True)
        date_field.value = value

        with pytest.raises(exception):
            date_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                '11.11.1111',
                '01.01.0001',
                '01.04.1970',
                '01.1.2022',
                '1.01.2022',  # datetime.datetime.strptime with %d will add missing zeros

            ]
    )
    def test_valid_date_field(self, value):
        date_field = apiscoring.api.DateField(required=False, nullable=True)
        date_field.value = value

        assert date_field.validate_field()


class TestBirthDayField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', ValueError),
                ('some.another.string', ValueError),
                ('1.2.3', ValueError),
                ('198.162.1.22', ValueError),
                ('01.01.2035', ValueError),
                ('32.12.2022', ValueError),
                ('45.05.2005', ValueError),
                ('01/01/2022', ValueError),
                ('99.99.9999', ValueError),
                ('06.07.1952', ValueError),
            ]
    )
    def test_none_valid_birthday_field(self, value, exception):
        birthday_field = apiscoring.api.BirthDayField(required=False, nullable=True)
        birthday_field.value = value

        with pytest.raises(exception):
            birthday_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                '10.07.1963',
                '01.04.1970',
                '01.1.2022',
                '1.01.2002',
            ]
    )
    def test_valid_birthday_field(self, value):
        birthday_field = apiscoring.api.BirthDayField(required=False, nullable=True)
        birthday_field.value = value

        assert birthday_field.validate_field()


class TestGenderField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, ValueError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', TypeError),
                ('some.another.string', TypeError),
                ('1.2.3', TypeError),
                (-1, ValueError),
                (5, ValueError),
            ]
    )
    def test_none_valid_gender_field(self, value, exception):
        gender_field = apiscoring.api.GenderField(required=False, nullable=True)
        gender_field.value = value

        with pytest.raises(exception):
            gender_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                0,
                1,
                2,
            ]
    )
    def test_valid_gender_field(self, value):
        gender_field = apiscoring.api.GenderField(required=False, nullable=True)
        gender_field.value = value

        assert gender_field.validate_field()


class TestClientIDsField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ({'oiug&khkjh': 2222}, TypeError),
                ('somestring', TypeError),
                ('some.another.string', TypeError),
                ('1.2.3', TypeError),
                (-1, TypeError),
                (5, TypeError),
                ([], ValueError),
                (['1', '2'], TypeError),
            ]
    )
    def test_none_valid_client_ids_field(self, value, exception):
        client_ids_field = apiscoring.api.ClientIDsField(required=True, nullable=False)
        client_ids_field.value = value

        with pytest.raises(exception):
            client_ids_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                [0, ],
                [2, 22, 222],
            ]
    )
    def test_valid_client_ids_field(self, value):
        client_ids_field = apiscoring.api.ClientIDsField(required=True, nullable=False)
        client_ids_field.value = value

        assert client_ids_field.validate_field()


class TestArgumentField:
    @pytest.mark.parametrize(
            'value, exception',
            [
                (121231321, TypeError),
                (('oiug&khkjh',), TypeError),
                ('somestring', TypeError),
                ('some.another.string', TypeError),
                ('1.2.3', TypeError),
                (-1, TypeError),
                (5, TypeError),
                ([], TypeError),
                (['1', '2'], TypeError),
            ]
    )
    def test_none_valid_argument_field(self, value, exception):
        argument_field = apiscoring.api.ArgumentsField(required=True, nullable=True)
        argument_field.value = value

        with pytest.raises(exception):
            argument_field.validate_field()

    @pytest.mark.parametrize(
            'value',
            [
                {'key': [0, ]},
                {},
            ]
    )
    def test_valid_argument_field(self, value):
        argument_field = apiscoring.api.ArgumentsField(required=True, nullable=True)
        argument_field.value = value

        assert argument_field.validate_field()