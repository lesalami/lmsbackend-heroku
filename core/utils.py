"""
Utilities for the core
"""
from enum import Enum
from psycopg2.extras import DateRange
from datetime import date
import calendar


def get_upload_path(instance, filename):
    """Dynamic file upload location"""
    return "{}/{}/{}".format(
        instance.organization.name,
        instance.file_type, filename
    )


def get_payrun_period():
    """Return default date range to the period"""
    day_1 = date.today().replace(day=1)
    last_day = calendar.monthrange(date.today().year, date.today().month)[1]
    last_day_date = date.today().replace(day=last_day)
    return DateRange(lower=day_1, upper=last_day_date)


class UserType(Enum):
    Parent = "Parent"
    Staff = "Staff"
    Admin = "Admin"
    Headmaster = "Headmaster"
    Proprietor = "Proprietor"
    Accountant = "Accountant"


user_type_choices = (
    ("Parent", "Parent"),
    ("Staff", "Staff"),
    ("Admin", "Admin"),
    ("Headmaster", "Headmaster"),
    ("Proprietor", "Proprietor"),
    ("Accountant", "Accountant"),
)


class EmploymentType(Enum):
    Full_Time = "Full Time"
    Part_Time = "Part Time"
    Contract = "Contract"
    Internship = "Internship"
    Other = "Other"


employment_type_choices = (
    ("Full Time", "Full Time"),
    ("Part Time", "Part Time"),
    ("Contract", "Contract"),
    ("Internship", "Internship"),
    ("Other", "Other")
)


class ResidencyChoices(Enum):
    Non_Resident = "Non-Resident"
    Resident_Part_Time = "Resident-Part-Time"
    Resident_Casual = "Resident_Casual"
    Resident_Full_Time = "Resident-Full-Time"


residency_choices = (
    ("Non-Resident", "Non-Resident"),
    ("Resident-Part-Time", "Resident-Part-Time"),
    ("Resident-Casual", "Resident-Casual"),
    ("Resident-Full-Time", "Resident-Full-Time")
)


class StaffType(Enum):
    Teaching = "Teaching"
    Non_Teaching = "Non-Teaching"


staff_type_choices = (
    ("Teaching", "Teaching"),
    ("Non-Teaching", "Non-Teaching")
)


class PaymentType(Enum):
    Invoice = "Invoice"
    Petty_cash = "Petty Cash"


payment_type_choices = (
    ("Invoice", "Invoice"),
    ("Petty Cash", "Petty Cash")
)


class PaymentMethod(Enum):
    Mobile_money = "Money money"
    Bank = "Bank"
    Cash = "Cash"


class GenderChoices(Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


class DocumentTypeChoices(Enum):
    Income = "Income"
    Expenditure = "Expenditure"
    Invoice = "Invoice"


class InvoiceStatus(Enum):
    Paid = "Paid"
    Owing = "Owing"
    Overdue = "Overdue"
    Partial = "Partial"


class PayrollRunStatus(Enum):
    Draft = "Draft"
    Processed = "Processed"
    Approved = "Approved"


CUSTOM_MESSAGES = {
    ('User', 'Create'): "{} was created",
    ('User', 'Update'): "{} details were updated for {}",
    ('User', 'Delete'): "The user {} was deleted.",
    ('Student', 'Create'): "{} was created as a student.",
    ('Student', 'Update'): "{} details were updated for Student {}",
    ('Student', 'Delete'): "Student {} was deleted.",
    ('Teacher', 'Create'): "{} was created as a teacher.",
    ('Teacher', 'Update'): "{} details were updated for Teacher {}",
    ('Teacher', 'Delete'): "Teacher {} was deleted.",
    ('ParentOrGuardian', 'Create'): "{} was created as a Parent",
    ('ParentOrGuardian', 'Update'): "{} details were updated for Parent {}",
    ('ParentOrGuardian', 'Delete'): "Parent {} was deleted",
    ('Subject', 'Create'): "{} Subject was created.",
    ('Subject', 'Update'): "{} details were updated for Subject {}",
    ('Subject', 'Delete'): "Subject {} was deleted.",
    ('Class', 'Create'): "Class {} was created.",
    ('Class', 'Update'): "{} details were updated for Class {}",
    ('Class', 'Delete'): "Class {} was deleted.",
    ('Invoice', 'Create'): "Invoice {} was created",
    ('Invoice', 'Update'): "{} details were updated for invoice {}",
    ('Invoice', 'Delete'): "Invoice {} was deleted",
    ('Income', 'Create'): "Income {} was created",
    ('Income', 'Update'): "{} details were updated for income {}",
    ('Income', 'Delete'): "Income {} was deleted",
    ('Expenditure', 'Create'): "Expenditure {} was created",
    ('Expenditure', 'Update'): "{} details were updated for expenditure {}",
    ('Expenditure', 'Delete'): "Expenditure {} was deleted",
    ('Receipt', 'Create'): "{} receipt was created",
    ('Receipt', 'Update'): "{} details were updated for receipt {}",
    ('Receipt', 'Delete'): "Receipt {} was deleted",
}


countries_choices = (
  ("AF", "Afghanistan"),
  ("AL", "Albania"),
  ("DZ", "Algeria"),
  ("AS", "American Samoa"),
  ("AD", "Andorra"),
  ("AO", "Angola"),
  ("AI", "Anguilla"),
  ("AG", "Antigua and Barbuda"),
  ("AR", "Argentina"),
  ("AM", "Armenia"),
  ("AW", "Aruba"),
  ("AU", "Australia"),
  ("AT", "Austria"),
  ("AZ", "Azerbaijan"),
  ("BS", "Bahamas"),
  ("BH", "Bahrain"),
  ("BD", "Bangladesh"),
  ("BB", "Barbados"),
  ("BY", "Belarus"),
  ("BE", "Belgium"),
  ("BZ", "Belize"),
  ("BJ", "Benin"),
  ("BM", "Bermuda"),
  ("BT", "Bhutan"),
  ("BO", "Bolivia, Plurinational State of"),
  ("BA", "Bosnia and Herzegovina"),
  ("BW", "Botswana"),
  ("BR", "Brazil"),
  ("IO", "British Indian Ocean Territory"),
  ("BG", "Bulgaria"),
  ("BF", "Burkina Faso"),
  ("BI", "Burundi"),
  ("KH", "Cambodia"),
  ("CM", "Cameroon"),
  ("CA", "Canada"),
  ("CV", "Cape Verde"),
  ("KY", "Cayman Islands"),
  ("CF", "Central African Republic"),
  ("TD", "Chad"),
  ("CL", "Chile"),
  ("CN", "China"),
  ("CO", "Colombia"),
  ("KM", "Comoros"),
  ("CG", "Congo"),
  ("CD", "Democratic Republic of the Congo"),
  ("CK", "Cook Islands"),
  ("CR", "Costa Rica"),
  ("CI", "Côte d'Ivoire"),
  ("HR", "Croatia"),
  ("CU", "Cuba"),
  ("CW", "Curaçao"),
  ("CY", "Cyprus"),
  ("CZ", "Czech Republic"),
  ("DK", "Denmark"),
  ("DJ", "Djibouti"),
  ("DM", "Dominica"),
  ("DO", "Dominican Republic"),
  ("EC", "Ecuador"),
  ("EG", "Egypt"),
  ("SV", "El Salvador"),
  ("GQ", "Equatorial Guinea"),
  ("ER", "Eritrea"),
  ("EE", "Estonia"),
  ("ET", "Ethiopia"),
  ("FK", "Falkland Islands (Malvinas)"),
  ("FO", "Faroe Islands"),
  ("FJ", "Fiji"),
  ("FI", "Finland"),
  ("FR", "France"),
  ("PF", "French Polynesia"),
  ("GA", "Gabon"),
  ("GM", "Gambia"),
  ("GE", "Georgia"),
  ("DE", "Germany"),
  ("GH", "Ghana"),
  ("GI", "Gibraltar"),
  ("GR", "Greece"),
  ("GL", "Greenland"),
  ("GD", "Grenada"),
  ("GU", "Guam"),
  ("GT", "Guatemala"),
  ("GG", "Guernsey"),
  ("GN", "Guinea"),
  ("GW", "Guinea-Bissau"),
  ("HT", "Haiti"),
  ("HN", "Honduras"),
  ("HK", "Hong Kong"),
  ("HU", "Hungary"),
  ("IS", "Iceland"),
  ("IN", "India"),
  ("ID", "Indonesia"),
  ("IR", "Iran, Islamic Republic of"),
  ("IQ", "Iraq"),
  ("IE", "Ireland"),
  ("IM", "Isle of Man"),
  ("IL", "Israel"),
  ("IT", "Italy"),
  ("JM", "Jamaica"),
  ("JP", "Japan"),
  ("JE", "Jersey"),
  ("JO", "Jordan"),
  ("KZ", "Kazakhstan"),
  ("KE", "Kenya"),
  ("KI", "Kiribati"),
  ("KP", "North Korea"),
  ("KR", "South Korea"),
  ("KW", "Kuwait"),
  ("KG", "Kyrgyzstan"),
  ("LA", "Lao People's Democratic Republic"),
  ("LV", "Latvia"),
  ("LB", "Lebanon"),
  ("LS", "Lesotho"),
  ("LR", "Liberia"),
  ("LY", "Libya"),
  ("LI", "Liechtenstein"),
  ("LT", "Lithuania"),
  ("LU", "Luxembourg"),
  ("MO", "Macao"),
  ("MK", "Republic of Macedonia"),
  ("MG", "Madagascar"),
  ("MW", "Malawi"),
  ("MY", "Malaysia"),
  ("MV", "Maldives"),
  ("ML", "Mali"),
  ("MT", "Malta"),
  ("MH", "Marshall Islands"),
  ("MQ", "Martinique"),
  ("MR", "Mauritania"),
  ("MU", "Mauritius"),
  ("MX", "Mexico"),
  ("FM", "Micronesia, Federated States of"),
  ("MD", "Republic of Moldova"),
  ("MC", "Monaco"),
  ("MN", "Mongolia"),
  ("ME", "Montenegro"),
  ("MS", "Montserrat"),
  ("MA", "Morocco"),
  ("MZ", "Mozambique"),
  ("MM", "Myanmar"),
  ("NA", "Namibia"),
  ("NR", "Nauru"),
  ("NP", "Nepal"),
  ("NL", "Netherlands"),
  ("NZ", "New Zealand"),
  ("NI", "Nicaragua"),
  ("NE", "Niger"),
  ("NG", "Nigeria"),
  ("NU", "Niue"),
  ("NF", "Norfolk Island"),
  ("MP", "Northern Mariana Islands"),
  ("NO", "Norway"),
  ("OM", "Oman"),
  ("PK", "Pakistan"),
  ("PW", "Palau"),
  ("PS", "Palestinian Territory"),
  ("PA", "Panama"),
  ("PG", "Papua New Guinea"),
  ("PY", "Paraguay"),
  ("PE", "Peru"),
  ("PH", "Philippines"),
  ("PN", "Pitcairn"),
  ("PL", "Poland"),
  ("PT", "Portugal"),
  ("PR", "Puerto Rico"),
  ("QA", "Qatar"),
  ("RO", "Romania"),
  ("RU", "Russia"),
  ("RW", "Rwanda"),
  ("KN", "Saint Kitts and Nevis"),
  ("LC", "Saint Lucia"),
  ("WS", "Samoa"),
  ("SM", "San Marino"),
  ("ST", "Sao Tome and Principe"),
  ("SA", "Saudi Arabia"),
  ("SN", "Senegal"),
  ("RS", "Serbia"),
  ("SC", "Seychelles"),
  ("SL", "Sierra Leone"),
  ("SG", "Singapore"),
  ("SX", "Sint Maarten"),
  ("SK", "Slovakia"),
  ("SI", "Slovenia"),
  ("SB", "Solomon Islands"),
  ("SO", "Somalia"),
  ("ZA", "South Africa"),
  ("SS", "South Sudan"),
  ("ES", "Spain"),
  ("LK", "Sri Lanka"),
  ("SD", "Sudan"),
  ("SR", "Suriname"),
  ("SZ", "Swaziland"),
  ("SE", "Sweden"),
  ("CH", "Switzerland"),
  ("SY", "Syria"),
  ("TW", "Taiwan"),
  ("TJ", "Tajikistan"),
  ("TZ", "Tanzania"),
  ("TH", "Thailand"),
  ("TG", "Togo"),
  ("TK", "Tokelau"),
  ("TO", "Tonga"),
  ("TT", "Trinidad and Tobago"),
  ("TN", "Tunisia"),
  ("TR", "Turkey"),
  ("TM", "Turkmenistan"),
  ("TC", "Turks and Caicos Islands"),
  ("TV", "Tuvalu"),
  ("UG", "Uganda"),
  ("UA", "Ukraine"),
  ("AE", "United Arab Emirates"),
  ("GB", "United Kingdom"),
  ("US", "United States"),
  ("UY", "Uruguay"),
  ("UZ", "Uzbekistan"),
  ("VU", "Vanuatu"),
  ("VE", "Venezuela, Bolivarian Republic of"),
  ("VN", "Viet Nam"),
  ("VI", "Virgin Islands"),
  ("YE", "Yemen"),
  ("ZM", "Zambia"),
  ("ZW", "Zimbabwe"),
)

