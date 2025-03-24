import Document, { Html, Head, Main, NextScript } from 'next/document'

class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
          {/* Add any additional meta tags, fonts, or scripts here */}
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
          <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet" />
          <meta name="description" content="Leela - A meta-creative intelligence system designed to generate truly innovative outputs that transcend conventional thinking." />
        </Head>
        <body>
          <Main />
          <NextScript />
          {/* Scripts can be added here if needed */}
        </body>
      </Html>
    )
  }
}

export default MyDocument