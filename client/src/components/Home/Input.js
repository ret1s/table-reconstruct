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
          <GridItem
            colSpan={4}
            bg="white"
            borderRadius="10px"
            borderWidth="1px"
          >
            <Center fontSize="25" fontWeight={1000} mt="10px">
              Input Image
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

            {result && result.vis_det && (
              <Zoom>
                <Center>
                  <Image boxSize="90%" src={result.vis_det} />
                </Center>
              </Zoom>
            )}
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
