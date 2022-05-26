from jft.string.char.is_digit import f as is_digit
from jft.string.char.is_upper import f as is_upper

# camel_to_snake
f = lambda ζ: (
  ('_' if is_digit(ζ[0]) else '')+ ζ[0].lower() + ''.join([
    f'_{ζ[θ].lower()}' if all([
      any([
        is_upper(ζ[θ]),
        is_digit(ζ[θ]),
        is_digit(ζ[θ-1]),
      ]),
      not all([
        is_digit(ζ[θ]),
        is_digit(ζ[θ-1]),
      ])
    ]) else f'{ζ[θ].lower()}'
    for θ in range(1, len(ζ))
  ])
)

def t():
  observation = f("ThisIsAnExampleOfCamelCase")
  expectation = "this_is_an_example_of_camel_case"
  return observation == expectation
