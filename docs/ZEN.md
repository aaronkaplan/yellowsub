### Zen and some preliminary thoughts on simplicity

This code follows a couple of principles which **MUST** be followed, in order to remain simple:

  * we *strictly* follow the **KISS** principle: keep it simple and stupid.
    * we **RE-USE** existing systems (RabbitMQ, SQS, etc.). NO NOT INVENT YOUR OWN.
    * the only reason for code is to interface-bridge these existing systems.
    * re-using existing systems should go via configuration settings.
    * if that's not possible, make **very simple** interface / glue code.
    * highly readable code is a MUST.
    * this means: less code is a MUST. Here are some rules of thumbs to check for simplicity:
      1. An interface code should not use more than 200 lines of code.
      2. It MUST have python docstyle explanations.
      3. It MUST have unit tests
      4. It MUST be explainable to a newcomer but average python coder in 15 mins. max.
      5. As a test, this newcomer python coder should be able to adapt something in the code in half a day.

  * Remember: *re-using existing systems* and simply interfacing them wins.

Code tends to become too complex over time. Then it's time to re-factor and simplify. Don't shy away from
*not* implementing things which no-one needs anyway. Observe carefully which functions are actually used in a system.
