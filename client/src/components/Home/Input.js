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
  useMultiStyleConfig
} from '@chakra-ui/react';
import Zoom from 'react-medium-image-zoom';
import Preloader from '../Pre';
import 'react-medium-image-zoom/dist/styles.css';
import {
  SpreadsheetComponent,
  SheetsDirective,
  SheetDirective,
  RowsDirective,
  RowDirective,
  CellsDirective,
  CellDirective,
} from '@syncfusion/ej2-react-spreadsheet';


function InputSection() {
  const [inputImage, setInputImage] = useState();
  const [result, setResult] = useState();
  const [state, setState] = useState('idle');

  function handleImageChange(e) {
    console.log(e.target.files[0]);
    setInputImage(e.target.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!inputImage) {
      setState('idle');
      return;
    }

    setState('working');

    console.log(inputImage);
    console.log(URL.createObjectURL(inputImage));

    const formData = new FormData();
    formData.append('image', inputImage);

    for (const value of formData.values()) {
      console.log(value);
    }

    try {
      const response = await axios.post('/api/upload', formData);
      console.log(response.data);
      setResult(response.data.result);
    } catch(error) {
      console.log(Object.keys(error), error.message);
    }

    setState('idle');
  }

  const renderResult =
    result &&
    result.tables &&
    result.tables.map((data, id) => {
      return (
        <Stack spacing={6}>
          <Heading fontFamily={'Abel Pro'} as="h4" size="md" noOfLines={1}>
            Table {id + 1}
          </Heading>
          <Grid minH="100%" templateColumns="repeat(4, 1fr)" gap={4}>
            <GridItem bg="white" borderRadius="10px" borderWidth="1px">
              <Center fontSize="20" fontWeight={1000} mt="10px">
                Table Image
              </Center>

              {data && data.vis_img && (
                <Zoom>
                  <Center>
                    <Image boxSize="90%" src={data.vis_img} />
                  </Center>
                </Zoom>
              )}
            </GridItem>
            <GridItem bg="white" borderRadius="10px" borderWidth="1px">
              <Center fontSize="20" fontWeight={1000} mt="10px">
                OCR Result
              </Center>

              {data && data.vis_ocr_img && (
                <Zoom>
                  <Center>
                    <Image boxSize="90%" src={data.vis_ocr_img} />
                  </Center>
                </Zoom>
              )}
            </GridItem>
            <GridItem bg="white" borderRadius="10px" borderWidth="1px">
              <Center fontSize="20" fontWeight={1000} mt="10px">
                Structure Result
              </Center>
              {data && data.vis_str_img && (
                <Zoom>
                  <Center>
                    <Image boxSize="90%" src={data.vis_str_img} />
                  </Center>
                </Zoom>
              )}
            </GridItem>
            <GridItem bg="white" borderRadius="10px" borderWidth="1px">
              <Center fontSize="20" fontWeight={1000} mt="10px">
                Cells Result
              </Center>

              {data && data.vis_cells_img && (
                <Zoom>
                  <Center>
                    <Image boxSize="90%" src={data.vis_cells_img} />
                  </Center>
                </Zoom>
              )}
            </GridItem>
          </Grid>

          <SpreadsheetComponent
            allowSave={true}
            saveUrl="https://services.syncfusion.com/react/production/api/spreadsheet/save"
          >
            <SheetsDirective>
              <SheetDirective name={'Table'}>
                <RowsDirective>
                  {data.cells_data &&
                    data.cells_data.map((row, _) => {
                      return (
                        <RowDirective>
                          <CellsDirective>
                            {row.map((cell, _) => {
                              return (
                                <CellDirective
                                  value={cell.value}
                                  rowSpan={cell.rowSpan}
                                  colSpan={cell.colSpan}
                                ></CellDirective>
                              );
                            })}
                          </CellsDirective>
                        </RowDirective>
                      );
                    })}
                </RowsDirective>
              </SheetDirective>
            </SheetsDirective>
          </SpreadsheetComponent>
        </Stack>
      );
    });

  return (
    <section>
<<<<<<< HEAD
      <Stack spacing={6}>
        <Grid minH="100%" templateColumns="repeat(9, 1fr)" gap={4}>
          <GridItem
            borderRadius="10px"
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
                  <Input maxW="250px" type="file" accept="image/*" 
                   sx={{
                    "::file-selector-button": {
                      height: 10,
                      padding: 0,
                      mr: 4,
                      ml: -4,
                      px: 2,
                      // background: "none",
                      border: "none",
                      fontWeight: "bold",
                    },
                  }}
                  />
                </Center>
              </FormControl>
              <Center>
                <Button
                  type="submit"
                  colorScheme="teal"
                  variant="solid"
                  mt="10px"
                  fontWeight={'normal'}
                  bg='#26a69a'
                  _hover={{ bg: 'green.500' }}
                >
                  Submit
                </Button>
              </Center>
            </form>
          </GridItem>
          <GridItem
            colSpan={4}
            bg="white"
            borderRadius="10px"
            borderWidth="1px"
          >
            <Center fontSize="25" fontWeight={1000} mt="10px">
              Input Image
=======
      <Grid
        mt='-100px'
        mb='-200px'
        h='500px'
        templateColumns='repeat(9, 1fr)'
        gap={4}
      >
        <GridItem borderRadius='lg' borderWidth='1px' h='145px' w='270px' bg='white'>
        <form onSubmit={handleSubmit} onChange={handleImageChange}>
          <FormControl >
            <Center>
              <FormLabel fontWeight={1000} mt='10px'>Upload Image</FormLabel>
>>>>>>> main
            </Center>

            {inputImage && (
              <Zoom>
                <Center>
                  <Image boxSize="90%" src={URL.createObjectURL(inputImage)} />
                </Center>
              </Zoom>
            )}
          </GridItem>
          <GridItem
            colSpan={4}
            bg="white"
            borderRadius="10px"
            borderWidth="1px"
          >
            <Center fontSize="25" fontWeight={1000} mt="10px">
              Detected Tables
            </Center>

            {state == 'idle' ? result && result.vis_det && (
              <Zoom>
                <Center>
                  <Image boxSize="90%" src={result.vis_det} />
                </Center>
              </Zoom>
            ) : <Preloader load={true} />}
          </GridItem>
        </Grid>

        {result && (
          <Heading fontFamily={'Abel Pro'} as="h1" size="xl" noOfLines={1}>
            Found {result.num_tables} tables
          </Heading>
        )}

        {renderResult}
      </Stack>
    </section>
  );
}

export default InputSection;