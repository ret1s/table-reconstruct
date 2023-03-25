import React from 'react';
import { useForm } from 'react-hook-form';

function Input() {
  const { register, handleSubmit } = useForm({ mode: "all" });
  const onSubmit = (data) => console.log(JSON.stringify(data));

  return (
    <form>
      <input
        {...register("firstName", { required: true })}
        placeholder="First name"
      />
      <br></br>
      <input
        {...register("lastName", { required: true })}
        placeholder="Last name"
      />
      <br></br>
      <input {...register("picture", { required: true })} type="file" />
      <br></br>
      <button type="button" onClick={handleSubmit(onSubmit)}>
        Submit
      </button>
    </form>
  );
}

export default Input;

