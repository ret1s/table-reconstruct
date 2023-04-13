import React, { useState } from 'react';
import axios from 'axios';
import {
  Button,
  Grid,
  GridItem,
  FormControl,
  FormLabel,
  Input,
  Center,
  Image,
  Heading,
  Stack,
} from '@chakra-ui/react';
import Zoom from 'react-medium-image-zoom';
import 'react-medium-image-zoom/dist/styles.css';

function InputSection() {
  const [inputImage, setInputImage] = useState();
  const [result, setResult] = useState();

  function handleImageChange(e) {
    console.log(e.target.files[0]);
    setInputImage(e.target.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    console.log(inputImage);
    console.log(URL.createObjectURL(inputImage));

    const formData = new FormData();
    formData.append('image', inputImage);

    for (const value of formData.values()) {
      console.log(value);
    }

    const response = await axios.post('/api/upload', formData);
    console.log(response.data);
    setResult(response.data.result);
  }

  const renderResult =
    result &&
    result.tables &&
    result.tables.map((data, id) => {
      return (
        <Stack spacing={6}>
          <Heading as="h2" noOfLines={1}>
            Table {id + 1}
          </Heading>
          <Grid minH="500px" templateColumns="repeat(4, 1fr)" gap={4}>
            <GridItem bg="white" orderRadius="lg" borderWidth="1px">
              <Center fontSize="25" fontWeight={1000} mt="10px">
                Table Image
              </Center>
              <Center>
                {data && data.vis_img && (
                  <Zoom>
                    <Image boxSize="90%" src={data.vis_img} />
                  </Zoom>
                )}
              </Center>
            </GridItem>
            <GridItem bg="white" orderRadius="lg" borderWidth="1px">
              <Center fontSize="25" fontWeight={1000} mt="10px">
                OCR Result
              </Center>
              <Center>
                {data && data.vis_ocr_img && (
                  <Zoom>
                    <Image boxSize="90%" src={data.vis_ocr_img} />
                  </Zoom>
                )}
              </Center>
            </GridItem>
            <GridItem bg="white" orderRadius="lg" borderWidth="1px">
              <Center fontSize="25" fontWeight={1000} mt="10px">
                Structure Result
              </Center>
              <Center>
                {data && data.vis_str_img && (
                  <Zoom>
                    <Image boxSize="90%" src={data.vis_str_img} />
                  </Zoom>
                )}
              </Center>
            </GridItem>
            <GridItem bg="white" orderRadius="lg" borderWidth="1px">
              <Center fontSize="25" fontWeight={1000} mt="10px">
                Cells Result
              </Center>
              <Center>
                {data && data.vis_cells_img && (
                  <Zoom>
                    <Image boxSize="90%" src={data.vis_cells_img} />
                  </Zoom>
                )}
              </Center>
            </GridItem>
          </Grid>
        </Stack>
      );
    });

  return (
    <section>
      <Stack spacing={6}>
        <Grid minH="500px" templateColumns="repeat(9, 1fr)" gap={4}>
          <GridItem
            borderRadius="lg"
            borderWidth="1px"
            h="145px"
            w="270px"
            bg="white"
          >
            <form onSubmit={handleSubmit} onChange={handleImageChange}>
              <FormControl>
                <Center>
                  <FormLabel fontWeight={1000} mt="10px">
                    Upload Image
                  </FormLabel>
                </Center>
                <Center>
                  <Input maxW="250px" type="file" accept="image/*" />
                </Center>
              </FormControl>
              <Center>
                <Button
                  type="submit"
                  colorScheme="teal"
                  variant="solid"
                  mt="10px"
                >
                  Submit
                </Button>
              </Center>
            </form>
          </GridItem>
          <GridItem colSpan={4} bg="white" orderRadius="lg" borderWidth="1px">
            <Center fontSize="25" fontWeight={1000} mt="10px">
              Input Image
            </Center>
            <Center>
              {inputImage && (
                <Zoom>
                  <Image boxSize="90%" src={URL.createObjectURL(inputImage)} />
                </Zoom>
              )}
            </Center>
          </GridItem>
          <GridItem colSpan={4} bg="white" orderRadius="lg" borderWidth="1px">
            <Center fontSize="25" fontWeight={1000} mt="10px">
              Detected Tables
            </Center>
            <Center>
              {result && result.vis_det && (
                <Zoom>
                  <Image boxSize="90%" src={result.vis_det} />
                </Zoom>
              )}
            </Center>
          </GridItem>
        </Grid>

        {result && (
          <Heading as="h1" noOfLines={1}>
            Found {result.num_tables} tables
          </Heading>
        )}

        {renderResult}
      </Stack>
    </section>
  );
}

export default InputSection;
