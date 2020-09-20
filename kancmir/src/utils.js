function escapeRegExChars(text) {
    const escapedChars = text.replace(/[-[\]{}()*+?.,\\^$|#]/g, '\\$&')
    return escapedChars.replace(/\s/g, '|')
}

export { escapeRegExChars }
