import React from 'react';
import { Container } from 'react-bootstrap';
import { Button } from '@chakra-ui/react';

function About() {
  return (
    <Container fluid className="about-section">
      <Container>
        <h1 className="project-heading">About</h1>
        <Button colorScheme='teal' variant='ghost'>
          Button
        </Button>
      </Container>
    </Container>
  );
}

export default About;
