import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { Button, ButtonGroup } from '@chakra-ui/react';

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
