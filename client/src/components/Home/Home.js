import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Input from './Input';

function Home() {
  return (
    <section>
      <Container fluid className="home-section" id="home">
        <Container fluid className="home-content">
          <Row>
            <Col md={6}>
              <div>
                <Input />
              </div>
            </Col>
            <Col md={6}></Col>
          </Row>
        </Container>
      </Container>
    </section>
  );
}

export default Home;
